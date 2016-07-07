import unittest

from django.test import TestCase as DjangoTestCase
from django.template import RequestContext
from django.template.loader import render_to_string

from django_enumfield import Enum, Item
from django_enumfield.utils import TemplateErrorException

from .enums import TestModelEnum
from .models import TestModel


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


class EnumConstructionTests(unittest.TestCase):
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

        self.enum = FooEnum

    def test_from_value(self):
        self.assertEqual(self.enum.from_value(10).slug, 'a')

    def test_from_slug(self):
        self.assertEqual(self.enum.from_slug('b').value, 20)

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


class TemplateTests(DjangoTestCase):
    def test_renders_template(self):
        ctx = RequestContext(HttpRequest())

        self.assertEqual(
            render_to_string('test.html', context_instance=ctx),
            "Item A, Item B\n",
        )

    def test_fails_loudly_for_invalid_app(self):
        ctx = RequestContext(HttpRequest())

        with self.assertRaises(TemplateErrorException):
            render_to_string('invalid.html', context_instance=ctx)

