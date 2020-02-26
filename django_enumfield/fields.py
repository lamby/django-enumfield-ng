from django.db import models


class EnumField(models.Field):
    def __init__(self, enum, *args, **kwargs):
        self.enum = enum

        kwargs.setdefault("choices", enum.get_choices())

        super(EnumField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "IntegerField"

    def to_python(self, value):
        return self.enum.to_python(value)

    def from_db_value(self, value, expression, connection, *args, **kwargs):
        return self.to_python(value)

    def get_prep_value(self, value):
        python_value = self.to_python(value)

        if python_value is None:
            return None

        return python_value.value

    def get_prep_lookup(self, lookup_type, value):
        def prepare(value):
            x = self.to_python(value)

            return self.get_prep_value(x)

        if lookup_type in ("exact", "lt", "lte", "gt", "gte"):
            return prepare(value)
        if lookup_type == "in":
            return [prepare(v) for v in value]
        if lookup_type == "isnull":
            return value

        raise TypeError("Lookup type %r not supported." % lookup_type)

    def value_to_string(self, obj):
        item = self.value_from_object(obj)
        return str(item.value)

    def clone(self):
        _, _, args, kwargs = self.deconstruct()
        return models.IntegerField(*args, **kwargs)

    def deconstruct(self):
        name, _, args, kwargs = super(EnumField, self).deconstruct()

        # If there is a callable default, override it and set the first item
        # from the enum. This is to stop randomised defaults causing unstable
        # migrations, as deconstruct is called every time makemigrations is run
        default = kwargs.get("default")
        if default and callable(default):
            kwargs["default"] = self.enum[0]

        try:
            kwargs["default"] = kwargs["default"].value
        except (KeyError, AttributeError):
            # No default or not an Item instance
            pass

        # We don't want to serialise this for migrations.
        del kwargs["choices"]

        return name, "django.db.models.IntegerField", args, kwargs
