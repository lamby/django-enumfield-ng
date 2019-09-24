import difflib

import six

from .item import Item


class NoSuchSlugValueError(ValueError):
    def __init__(self, slug, enum):
        self.slug = slug
        self.enum = enum
        super().__init__()

    def _message(self):
        valid_slugs = [x.slug for x in self.enum]

        if len(valid_slugs) <= 3:
            corrective_message = "Slugs: %s" % ", ".join(valid_slugs)
        else:
            best_matches = difflib.get_close_matches(self.slug, valid_slugs)
            corrective_message = "Close matches: %s" % ", ".join(best_matches)

        return "%r is not a valid slug for enum %s; %s" % (
            self.slug,
            self.enum.name,
            corrective_message,
        )

    __str__ = _message

    def repr(self):
        return "%s(%r)" % (type(self).__name__, self._message())


class Enum(list):
    def __init__(self, name, *items):
        self.name = name

        super(Enum, self).__init__()

        for x in items:
            self.add_item(x)

    def __repr__(self):
        return "<%s: %s>" % (self.name, list(self))

    def add_item(self, item):
        for name, fn, value in (
            ("value", self.from_value, item.value),
            ("slug", self.from_slug, item.slug),
        ):
            try:
                fn(value)
            except ValueError:
                pass
            else:
                raise ValueError("Duplicate item %s: %r" % (name, value))

        setattr(self, item.slug.upper(), item)

        self.append(item)

    def from_value(self, value):
        if not isinstance(value, int):
            # Allow values that convert to int, as we might be deserialising an
            # int value. Raises ValueError and falls through to_python
            # accordingly if this is not actually an int.
            value = int(value)

        try:
            return {x.value: x for x in self}[value]
        except KeyError:
            raise ValueError("%r is not a valid value for enum %s" % (value, self.name))

    def from_slug(self, slug):
        if not isinstance(slug, six.string_types):
            raise TypeError("item slug should be a str, not %r" % type(slug))

        try:
            return {x.slug.lower(): x for x in self}[slug.lower()]
        except KeyError:
            raise NoSuchSlugValueError(slug=slug, enum=self)

    def get_choices(self):
        return [(x, x.display) for x in self]

    def to_python(self, value):
        if value in (None, "", u""):
            return None

        if isinstance(value, Item):
            return value

        try:
            return self.from_value(value)
        except ValueError:
            pass

        try:
            return self.from_slug(value)
        except (ValueError, TypeError):
            pass

        raise ValueError(
            "%r is not a valid slug or value for enum %s" % (value, self.name)
        )
