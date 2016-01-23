django-enumfield
================

Instance based::

    FooEnum = Enum('FooEnum',
        Item(10, 'a', "Item A"),
        Item(20, 'b', "Item B"),
    )

Dynamically adding items::

    FooEnum = Enum('FooEnum')
    FooEnum.add_item(Item(10, 'a', "Item A"))
    FooEnum.add_item(Item(20, 'b', "Item B"))

Simple registry pattern::

    FooEnum = Enum('FooEnum')

    class A(Item):
        __enum__ = FooEnum

        value = 10
        display = "Item A"

    class B(Item):
        __enum__ = FooEnum

        value = 20
        display = "Item B"

Registry pattern with parent class::

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
