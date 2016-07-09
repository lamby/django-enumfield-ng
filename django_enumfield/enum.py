from .item import Item

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
            ('value', self.from_value, item.value),
            ('slug', self.from_slug, item.slug),
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
        try:
            return {x.value: x for x in self}[value]
        except KeyError:
            raise ValueError("%r is not a valid value for the enum" % value)

    def from_slug(self, slug):
        if not isinstance(slug, basestring):
            raise TypeError("item slug should be a str, not %r" % type(slug))

        try:
            return {x.slug.lower(): x for x in self}[slug.lower()]
        except KeyError:
            raise ValueError("%r is not a valid slug for the enum" % slug)

    def get_choices(self):
        return [(x, x.display) for x in self]

    def to_python(self, value):
        if value in (None, '', u''):
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

        raise ValueError("%r is not a valid slug or value for the enum" % value)
