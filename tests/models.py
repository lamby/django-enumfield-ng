from django_enumfield import EnumField, Enum, Item

from django.db import models


TestModelEnum = Enum(
    'TestModelEnum',
    Item(10, 'a', "Item A"),
    Item(20, 'b', "Item B"),
)


class TestModel(models.Model):
    test_field = EnumField(TestModelEnum, default=TestModelEnum.A)
    test_field_no_default = EnumField(TestModelEnum)
