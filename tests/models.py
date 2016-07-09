import random

from django_enumfield import EnumField

from django.db import models

from .enums import TestModelEnum


class TestModel(models.Model):
    test_field = EnumField(TestModelEnum, default=TestModelEnum.A)
    test_field_no_default = EnumField(TestModelEnum)


def random_default():
    return random.choice(TestModelEnum)


class TestModelRandomDefault(models.Model):
    test_field = EnumField(TestModelEnum, default=random_default)
