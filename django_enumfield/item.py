import functools

from .utils import is_lazy_translation
from .app_settings import app_settings


@functools.total_ordering
class Item:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        name = cls.__name__

        try:
            value = cls.value
        except AttributeError:
            pass
        else:
            slug = name
            if app_settings.EXPLICIT_SLUGS:
                if not hasattr(cls, "slug"):
                    raise TypeError("%r class must have a slug attribute" % name)
                slug = cls.slug

            item = cls(value, slug, getattr(cls, "display", None))
            cls.__enum__.add_item(item)

    def __init__(self, value, slug, display=None):
        if not isinstance(value, int):
            raise TypeError("item value should be an int, not %r" % type(value))

        if not isinstance(slug, str):
            raise TypeError("item slug should be a str, not %r" % type(slug))

        if (
            display is not None
            and not isinstance(display, str)
            and not is_lazy_translation(display)
        ):
            raise TypeError(
                "item display name should be a string or lazily evaluated "
                "string, not %r" % type(display)
            )

        self.value = value
        self.slug = slug
        self.display = display if display is not None else slug.capitalize()

    def __str__(self):
        return self.slug

    def __repr__(self):
        return "<enum.Item: %d %s %r>" % (self.value, self.slug, self.display)

    def __hash__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.value == other.value

        if isinstance(other, (int, str)):
            try:
                return self.value == int(other)
            except ValueError:
                return str(self.slug) == str(other)

        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if not isinstance(other, Item):
            return NotImplemented

        return self.value < other.value
