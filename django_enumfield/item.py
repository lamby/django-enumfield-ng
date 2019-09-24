import six
import functools

from .utils import is_lazy_translation
from .app_settings import app_settings


class ItemMeta(type):
    def __new__(mcs, name, bases, attrs):
        cls = super(ItemMeta, mcs).__new__(mcs, name, bases, attrs)

        try:
            value = attrs["value"]
        except KeyError:
            pass
        else:
            slug = name
            if app_settings.EXPLICIT_SLUGS:
                if "slug" not in attrs:
                    raise TypeError("%r class must have a slug attribute" % name)
                slug = attrs["slug"]

            item = cls(value, slug, attrs.get("display"))
            cls.__enum__.add_item(item)

        return cls


@functools.total_ordering
class Item(six.with_metaclass(ItemMeta, object)):
    def __init__(self, value, slug, display=None):
        if not isinstance(value, int):
            raise TypeError("item value should be an int, not %r" % type(value))

        if not isinstance(slug, str):
            raise TypeError("item slug should be a str, not %r" % type(slug))

        if (
            display is not None
            and not isinstance(display, six.string_types)
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
        return u"<enum.Item: %d %s %r>" % (self.value, self.slug, self.display)

    def __hash__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.value == other.value

        if isinstance(other, six.integer_types + six.string_types):
            try:
                return self.value == int(other)
            except ValueError:
                return six.text_type(self.slug) == six.text_type(other)

        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if not isinstance(other, Item):
            return NotImplemented

        return self.value < other.value
