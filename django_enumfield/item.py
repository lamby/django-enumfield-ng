class Item(object):
    def __init__(self, value, slug, display=None):
        if not isinstance(value, int):
            raise TypeError("item value should be an int, not %r" \
                % type(value))

        if not isinstance(slug, str):
            raise TypeError("item slug should be a str, not %r" % type(slug))

        if display is not None and not isinstance(display, basestring):
            raise TypeError("item display name should be a basestring, not %r" \
                % type(display))

        self.value = value
        self.slug = slug
        self.display = display if display is not None else slug.capitalize()

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
