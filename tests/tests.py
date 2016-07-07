import unittest

from django_enumfield import Enum, Item


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
