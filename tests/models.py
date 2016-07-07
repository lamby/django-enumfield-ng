from django_enumfield import EnumField

from django.db import models

from .enums import TestModelEnum


class TestModel(models.Model):
    test_field = EnumField(TestModelEnum, default=TestModelEnum.A)
    test_field_no_default = EnumField(TestModelEnum)
