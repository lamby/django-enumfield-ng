from django_enumfield import Enum, Item


TestModelEnum = Enum(
    'TestModelEnum',
    Item(10, 'a', "Item A"),
    Item(20, 'b', "Item B"),
)
