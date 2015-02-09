from .item import Item

class EnumerationMeta(type):
    def __new__(mcs, name, bases, attrs):
        items = []

        # Inherit items from parent classes
        for base in bases:
            if hasattr(base, 'items'):
                items.extend(base.items)

        slugs = set(x.slug for _, x in items)
        values = set(x.value for _, x in items)

        for n, item in list(attrs.items()):
            if not isinstance(item, Item):
                continue

            if item.value in values:
                raise ValueError(
                    "Item value %d has been used more than once (%s)" % \
                        (item.value, item)
                )
            if item.slug in slugs:
                raise ValueError(
                    "Item slug %r has been used more than once" % item.slug
                )

            items.append((n, item))
            slugs.add(item.slug)
            values.add(item.value)

        items.sort(key=lambda i: i[1].creation_counter)

        specials = {
            'items': items,
        }

        for k in specials.keys():
            assert k not in attrs, "%r is a forbidden Item name" % k

        attrs.update(specials)

        return super(EnumerationMeta, mcs).__new__(mcs, name, bases, attrs)

    def __iter__(mcs):
        return iter(x for _, x in mcs.items)

class EnumerationBase(object):
    @classmethod
    def from_value(cls, value):
        try:
            return {x.value: x for _, x in cls.items}[value]
        except KeyError:
            raise ValueError(
                "%r is not a valid value for the enumeration" % value
            )

    @classmethod
    def from_slug(cls, slug):
        try:
            return {x.slug: x for _, x in cls.items}[slug]
        except KeyError:
            raise ValueError(
                "%r is not a valid slug for the enumeration" % slug
            )

    @classmethod
    def to_python(cls, value):
        if value in (None, '', u''):
            return None

        if isinstance(value, Item):
            return value

        try:
            return cls.from_value(value)
        except ValueError:
            pass

        try:
            return cls.from_slug(value)
        except ValueError:
            pass

        raise ValueError(
            "%r is not a valid slug or value for the enumeration" % value
        )

    @classmethod
    def get_choices(cls):
        return [(x, x.display) for _, x in cls.items]

class Enumeration(EnumerationBase):
    __metaclass__ = EnumerationMeta

def make_enum(name, *items):
    """
    Returns an enumeration type compatible with Enumeration. Example:

    >>> FunnelStageEnum = make_enum('FunnelStageEnum',
        Item(10, 'landing'),
        Item(20, 'email'),
    )
    """

    return type(
        name,
        (Enumeration,),
        dict((i.slug.upper(), i) for i in items),
    )
