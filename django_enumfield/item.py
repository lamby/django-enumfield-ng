class ItemMeta(type):
    def __new__(mcs, name, bases, attrs):
        mcs.creation_counter = 0
        return super(ItemMeta, mcs).__new__(mcs, name, bases, attrs)

class Item(object):
    __metaclass__ = ItemMeta

    def __init__(self, value, slug, display=None):
        if not isinstance(value, int):
            raise TypeError("item value should be an int, not %r" \
                % type(value))

        if not isinstance(slug, str):
            raise TypeError("item slug should be a str, not %r" % type(slug))

        if display is not None and not isinstance(display, (basestring)):
            raise TypeError("item display name should be a basestring, not %r" \
                % type(display))

        super(Item, self).__init__()

        self.value = value
        self.slug = slug

        if display is None:
            self.display = slug.capitalize()
        else:
            self.display = display

        self.creation_counter = Item.creation_counter
        Item.creation_counter += 1

    def __repr__(self):
        return u"<enum.Item: %d %s %r>" % (self.value, self.slug, self.display)

    def __hash__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.value == other.value
        if isinstance(other, (int, str, long, unicode)):
            try:
                return self.value == int(other)
            except ValueError:
                return unicode(self.slug) == unicode(other)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)
