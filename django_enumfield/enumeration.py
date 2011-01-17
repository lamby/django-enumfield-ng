from .item import Item

class EnumerationMeta(type):
    def __new__(mcs, name, bases, attrs):
        used_values = set()
        used_slugs = set()
        items = []

        for n, item in list(attrs.items()):
            if isinstance(item, Item):
                if item.value in used_values:
                    raise ValueError(
                        "Item value %d has been used more than once (%s)" % \
                            (item.value, item)
                    )
                used_values.add(item.value)
                if item.slug in used_slugs:
                    raise ValueError(
                        "Item slug "%s" has been used more than once" % item.slug
                    )
                used_slugs.add(item.slug)

                items.append((n, item))

        items.sort(key=lambda i: i[1].value)
        item_objects = [i[1] for i in items]

        by_val = dict((i.value, i) for i in item_objects)
        by_slug = dict((i.slug, i) for i in item_objects)

        specials = {
            'items': dict(items),
            'sorted_items': items,
            'items_by_val': by_val,
            'items_by_slug': by_slug,
        }

        for k in specials.keys():
            assert k not in attrs, "%r is a forbidden Item name" % k

        attrs.update(specials)

        init_class = attrs.pop('init_class', None)
        cls = super(EnumerationMeta, mcs).__new__(mcs, name, bases, attrs)

        if init_class:
            init_class(cls)

        return cls

    def init_class(mcs):
        pass

    def __iter__(mcs):
        return (key_val for key_val in mcs.sorted_items)

    def __getitem__(mcs, prop):
        return mcs.items[prop]

class Enumeration(object):
    __metaclass__ = EnumerationMeta

    @classmethod
    def from_value(cls, value):
        return cls.items_by_val.get(value)

    @classmethod
    def from_slug(cls, slug):
        return cls.items_by_slug.get(slug)

    @classmethod
    def get_items(cls):
        return [i for n, i in cls]

    @classmethod
    def get_choices(cls):
        return [(item, item.display) for item in cls.get_items()]

    @classmethod
    def to_item(cls, value):
        if value in (None, '', u''):
            return None

        if isinstance(value, Item):
            return value

        try:
            value = int(value)
            item = cls.from_value(value)
        except ValueError:
            item = cls.from_slug(value)

        if item:
            return item

        raise ValueError, "%s is not a valid value for the enumeration" % value
