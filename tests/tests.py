import unittest

from django.db import models
from django.db.utils import IntegrityError
from django.core import serializers
from django.http import HttpRequest, Http404
from django.test import TestCase as DjangoTestCase, override_settings
from django.template.loader import render_to_string
from django.db.models.fields import NOT_PROVIDED
from django.utils.translation import gettext_lazy as _

from django_enumfield import Enum, Item, get_enum_or_404
from django_enumfield.utils import TemplateErrorException

from .enums import TestModelEnum
from .models import TestModel, TestModelNull, TestModelRandomDefault


class ItemTests(unittest.TestCase):
    def test_item(self):
        item = Item(10, 'slug', "Display")

        self.assertEqual(item.value, 10)
        self.assertEqual(item.slug, 'slug')
        self.assertEqual(item.display, "Display")

    def test_invalid_types(self):
        with self.assertRaises(TypeError):
            Item('not an int', 'slug', "display")

        with self.assertRaises(TypeError):
            Item(10, 999, "display")

        with self.assertRaises(TypeError):
            Item(10, 'slug', 999)

    def test_str(self):
        self.assertEqual(str(Item(10, 'slug', "display")), 'slug')

    def test_repr(self):
        self.assertEqual(
            repr(Item(10, 'slug', "display")),
            "<enum.Item: 10 slug 'display'>",
        )

    def test_hash(self):
        self.assertEqual(hash(Item(10, 'slug', "display")), 10)

    def test_eq(self):
        item1 = Item(10, 'slug', "display")
        item2 = Item(10, 'slug', "display")
        item3 = Item(20, 'slug3', "display")

        self.assertEqual(item1, item2)
        self.assertNotEqual(item1, item3)

        self.assertEqual('slug', item1)
        self.assertEqual(item3, 'slug3')
        self.assertNotEqual(item2, 'slug2')

    def test_comparison(self):
        item1 = Item(10, 'slug1', "display1")
        item2 = Item(20, 'slug2', "display2")
        item2_copy = Item(20, 'slug2', "display2")

        self.assertLess(item1, item2)
        self.assertGreater(item2, item1)
        self.assertGreaterEqual(item2, item2_copy)
        self.assertLessEqual(item2, item2_copy)

    def test_lazy_translation_in_display(self):
        item = Item(10, 'slug', _("Display"))
        self.assertEqual(item.display, "Display")


class EnumConstructionTests(unittest.TestCase):
    longMessage = True

    def test_instance_based_enum(self):
        FooEnum = Enum(
            'FooEnum',
            Item(10, 'a', "Item A"),
            Item(20, 'b', "Item B"),
        )

        self.assertEqual(len(FooEnum), 2)
        self.assertEqual(FooEnum.A.slug, 'a')
        self.assertEqual(FooEnum.B.display, "Item B")
        self.assertEqual(FooEnum.from_value(10).slug, 'a')

    def test_dynamic_enum(self):
        FooEnum = Enum('FooEnum')
        FooEnum.add_item(Item(10, 'a', "Item A"))
        FooEnum.add_item(Item(20, 'b', "Item B"))

        self.assertEqual(len(FooEnum), 2)
        self.assertEqual(FooEnum.A.slug, 'a')
        self.assertEqual(FooEnum.B.display, "Item B")
        self.assertEqual(FooEnum.from_value(10).slug, 'a')

    def test_dynamic_enum_rejects_duplicate_value(self):
        FooEnum = Enum('FooEnum')
        FooEnum.add_item(Item(10, 'a', "Item A"))

        with self.assertRaises(ValueError):
            FooEnum.add_item(Item(10, 'b', "Item B"))

    def test_dynamic_enum_rejects_duplicate_slug(self):
        FooEnum = Enum('FooEnum')
        FooEnum.add_item(Item(10, 'a', "Item A"))

        with self.assertRaises(ValueError):
            FooEnum.add_item(Item(20, 'a', "Item B"))

    def test_simple_registry_enum(self):
        FooEnum = Enum('FooEnum')

        class A(Item):
            __enum__ = FooEnum

            value = 10
            display = "Item A"

        class B(Item):
            __enum__ = FooEnum

            value = 20
            display = "Item B"

        self.assertEqual(len(FooEnum), 2)
        self.assertEqual(FooEnum.A.slug, 'A')
        self.assertEqual(FooEnum.B.display, "Item B")
        self.assertEqual(FooEnum.from_value(10).slug, 'A')

    @override_settings(ENUMFIELD_EXPLICIT_SLUGS=True)
    def test_simple_registry_enum_with_explicit_slugs(self):
        FooEnum = Enum('FooEnum')

        class A(Item):
            __enum__ = FooEnum

            value = 10
            slug = 'item_a'
            display = "Item A"

        class B(Item):
            __enum__ = FooEnum

            value = 20
            slug = 'item_b'
            display = "Item B"

        self.assertEqual(len(FooEnum), 2)
        self.assertEqual(FooEnum.ITEM_A.slug, 'item_a')
        self.assertEqual(FooEnum.ITEM_B.display, "Item B")
        self.assertEqual(FooEnum.from_value(10).slug, 'item_a')

    @override_settings(ENUMFIELD_EXPLICIT_SLUGS=True)
    def test_slug_missing_with_explicit_slugs_s(self):
        FooEnum = Enum('FooEnum')

        # Should be able to create helpers which have neither slug nor value
        class FooItem(Item):
            __enum__ = FooEnum

        self.assertEqual(len(FooEnum), 0)

        with self.assertRaises(TypeError) as cm:
            class BadItem(Item):
                __enum__ = FooEnum

                value = 20
                display = "Item B"

        self.assertEqual(
            "'BadItem' class must have a slug attribute",
            str(cm.exception),
            "Wrong error message for missing slug",
        )

        self.assertEqual(len(FooEnum), 0)

    def test_registry_without_parent(self):
        FooEnum = Enum('FooEnum')

        class FooEnumItem(Item):
            __enum__ = FooEnum

            def display_extended(self):
                return "%s (%s)" % (self.display, self.value)

        class A(FooEnumItem):
            value = 10
            display = "Item A"

        class B(FooEnumItem):
            value = 20
            display = "Item B"

        self.assertEqual(len(FooEnum), 2)
        self.assertEqual(FooEnum.A.slug, 'A')
        self.assertEqual(FooEnum.B.display, "Item B")
        self.assertEqual(FooEnum.from_value(10).slug, 'A')

        self.assertEqual(FooEnum.A.display_extended(), "Item A (10)")


class EnumTests(unittest.TestCase):
    def setUp(self):
        super(EnumTests, self).setUp()

        FooEnum = Enum(
            'FooEnum',
            Item(10, 'a', "Item A"),
            Item(20, 'b', "Item B"),
        )

        LargeEnum = Enum(
            'LargeEnum',
            Item(10, 'item_a', "Item A"),
            Item(20, 'item_b', "Item B"),
            Item(30, 'item_c', "Item C"),
            Item(40, 'item_d', "Item D"),
            Item(50, 'item_e', "Item E"),
        )

        self.enum = FooEnum
        self.large_enum = LargeEnum

    def test_from_value(self):
        self.assertEqual(self.enum.from_value(10).slug, 'a')

        with self.assertRaises(ValueError):
            self.enum.from_value('a')

    def test_from_slug(self):
        self.assertEqual(self.enum.from_slug('b').value, 20)

        with self.assertRaises(TypeError):
            self.enum.from_slug(20)

        with self.assertRaises(ValueError) as cm:
            self.enum.from_slug('nope')

        self.assertIn(
            'nope',
            str(cm.exception),
            "Exception message should contain errenous slug",
        )

        self.assertIn(
            'a, b',
            str(cm.exception),
            "Exception message should contain valid slugs",
        )

        self.assertIn(
            self.enum.name,
            str(cm.exception),
            "Exception message should contain enum name",
        )

        with self.assertRaises(ValueError) as cm:
            self.large_enum.from_slug('item')

        self.assertIn(
            'item',
            str(cm.exception),
            "Exception message should contain errenous slug",
        )

        self.assertIn(
            'item_e, item_d, item_c',
            str(cm.exception),
            "Exception message should contain valid slugs",
        )

        self.assertIn(
            self.large_enum.name,
            str(cm.exception),
            "Exception message should contain enum name",
        )

    def test_get_choices(self):
        self.assertEqual(
            self.enum.get_choices(),
            [
                (Item(10, 'a', "Item A"), "Item A"),
                (Item(20, 'b', "Item B"), "Item B"),
            ],
        )

    def test_to_python(self):
        self.assertEqual(self.enum.to_python(''), None)
        self.assertEqual(self.enum.to_python(None), None)

        self.assertEqual(self.enum.to_python(self.enum.A), self.enum.A)

        self.assertEqual(self.enum.to_python(10), self.enum.A)
        self.assertEqual(self.enum.to_python(10), self.enum.A)

        self.assertEqual(self.enum.to_python('b'), self.enum.B)

        with self.assertRaises(ValueError):
            self.enum.to_python(999)

        with self.assertRaises(ValueError):
            self.enum.to_python('not_a_slug')

    def test_repr(self):
        self.assertEqual(
            repr(self.enum),
            "<FooEnum: [%r, %r]>" % (self.enum.A, self.enum.B),
        )


class FieldTests(DjangoTestCase):
    def assertCreated(self, num=1):
        self.assertEqual(TestModel.objects.count(), num)

    def test_model_instantiate(self):
        TestModel(
            test_field=TestModelEnum.A,
            test_field_no_default=TestModelEnum.B,
        )

    def test_model_creation(self):
        TestModel.objects.create(
            test_field=TestModelEnum.A,
            test_field_no_default=TestModelEnum.B,
        )

        self.assertCreated()

    def test_model_instantiate_using_defulat(self):
        TestModel(
            test_field_no_default=TestModelEnum.B,
        )

    def test_model_creation_using_defulat(self):
        TestModel.objects.create(
            test_field_no_default=TestModelEnum.B,
        )

        self.assertCreated()

    def test_model_instantiate_without_default(self):
        TestModel(
            test_field=TestModelEnum.A,
        )

    def test_model_creation_without_default(self):
        with self.assertRaises(IntegrityError):
            TestModel.objects.create(
                test_field=TestModelEnum.A,
            )

    def test_field_default(self):
        model = TestModel.objects.create(test_field_no_default=TestModelEnum.B)
        self.assertEqual(model.test_field, TestModelEnum.A)

    def test_field_from_slug(self):
        model = TestModel.objects.create(test_field_no_default='a')
        self.assertCreated()
        self.assertEqual(model.test_field_no_default, TestModelEnum.A)

    def test_field_from_value(self):
        model = TestModel.objects.create(test_field_no_default=20)
        self.assertCreated()
        self.assertEqual(model.test_field_no_default, TestModelEnum.B)

    def test_field_converts_to_python(self):
        model1 = TestModel(test_field_no_default='a')
        self.assertEqual(model1.test_field_no_default, TestModelEnum.A)

        model2 = TestModel(test_field_no_default=20)
        self.assertEqual(model2.test_field_no_default, TestModelEnum.B)

    def test_query(self):
        m1 = TestModel.objects.create(test_field_no_default=TestModelEnum.A)
        TestModel.objects.create(test_field_no_default=TestModelEnum.B)

        self.assertEqual(TestModel.objects.count(), 2)
        self.assertEqual(
            list(TestModel.objects.filter(
                test_field_no_default=TestModelEnum.A,
            )),
            [m1],
        )
        self.assertEqual(
            list(TestModel.objects.filter(
                test_field_no_default='a',
            )),
            [m1],
        )
        self.assertEqual(
            list(TestModel.objects.filter(
                test_field_no_default=10,
            )),
            [m1],
        )

    def test_null_field(self):
        TestModelNull.objects.create(test_field_null=None)

    def test_field_lookup(self):
        TestModelNull.objects.create(test_field_null=None)
        m2 = TestModelNull.objects.create(test_field_null=TestModelEnum.A)

        query = TestModelNull.objects.filter(
            test_field_null__in=(TestModelEnum.A, TestModelEnum.B),
        )

        self.assertEqual(list(query), [m2])

    def test_field_lookup_in_slugs(self):
        TestModelNull.objects.create(test_field_null=None)
        m2 = TestModelNull.objects.create(test_field_null=TestModelEnum.A)

        query = TestModelNull.objects.filter(test_field_null__in=('a', 'b'))

        self.assertEqual(list(query), [m2])

    def test_field_lookup_in_values(self):
        TestModelNull.objects.create(test_field_null=None)
        m2 = TestModelNull.objects.create(test_field_null=TestModelEnum.A)

        query = TestModelNull.objects.filter(test_field_null__in=(10, 20))

        self.assertEqual(list(query), [m2])

    def test_field_lookup_in_non_existent_slug_fails(self):
        with self.assertRaises(ValueError):
            TestModel.objects.filter(test_field__in=('not_a_slug',))

    def test_field_lookup_in_non_existent_value_fails(self):
        with self.assertRaises(ValueError):
            TestModel.objects.filter(test_field__in=(999,))

    def test_isnull(self):
        m1 = TestModelNull.objects.create(test_field_null=None)
        TestModelNull.objects.create(test_field_null=TestModelEnum.A)

        query = TestModelNull.objects.filter(test_field_null__isnull=True)

        self.assertEqual(list(query), [m1])


class TemplateTests(DjangoTestCase):
    def test_renders_template(self):
        self.assertEqual(
            render_to_string('test.html', {}, request=HttpRequest()),
            "Item A, Item B\n",
        )

    def test_fails_loudly_for_invalid_app(self):
        with self.assertRaises(TemplateErrorException):
            render_to_string('invalid.html', {}, request=HttpRequest())


class UtilsTests(unittest.TestCase):
    def test_get_enum_or_404_valid(self):
        self.assertEqual(
            get_enum_or_404(TestModelEnum, 'a'),
            TestModelEnum.A,
        )

    def test_get_enum_or_404_invalid(self):
        with self.assertRaises(Http404):
            get_enum_or_404(TestModelEnum, 'not_a_slug')


class MigrationUnitTests(DjangoTestCase):
    def assertDeconstruct(self, model_class, field, exp_args, exp_kwargs):
        model = model_class()
        name, path, args, kwargs = model._meta.get_field(field).deconstruct()
        self.assertEqual(name, field)
        self.assertEqual(path, 'django.db.models.IntegerField')
        self.assertEqual(args, exp_args)
        self.assertEqual(kwargs, exp_kwargs)

    def test_deconstruct(self):
        self.assertDeconstruct(TestModel, 'test_field', [], {'default': 10})

    def test_deconstruct_no_default(self):
        self.assertDeconstruct(TestModel, 'test_field_no_default', [], {})

    def test_deconstruct_null(self):
        self.assertDeconstruct(
            TestModelNull,
            'test_field_null',
            [],
            {'null': True},
        )

    def test_deconstruct_callable_default(self):
        self.assertDeconstruct(
            TestModelRandomDefault,
            'test_field',
            [],
            {'default': 10},
        )

    def test_field_clone(self):
        model = TestModel()
        field = model._meta.get_field('test_field_no_default')
        clone = field.clone()

        self.assertTrue(isinstance(clone, models.IntegerField))
        self.assertEqual(clone.default, NOT_PROVIDED)

    def test_field_clone_with_default(self):
        model = TestModel()
        field = model._meta.get_field('test_field')
        clone = field.clone()

        self.assertTrue(isinstance(clone, models.IntegerField))
        self.assertEqual(clone.default, 10)


class SerialisationTests(DjangoTestCase):
    def test_serialisation(self):
        m_in = TestModel.objects.create(test_field_no_default=TestModelEnum.B)

        data = serializers.serialize('xml', TestModel.objects.all())
        objects = serializers.deserialize('xml', data)

        m_out = next(objects).object

        self.assertEqual(m_in.pk, m_out.pk)
        self.assertEqual(m_in.test_field, m_out.test_field)
        self.assertEqual(
            m_in.test_field_no_default,
            m_out.test_field_no_default,
        )
