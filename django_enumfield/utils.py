import six

from django.http import Http404
from django.utils.functional import Promise


def get_enum_or_404(enum, slug):
    try:
        return enum.from_slug(slug)
    except ValueError:
        raise Http404()


class TemplateErrorDict(dict):
    """
    Like a regular dict but raises our own exception instead of ``KeyError`` to
    bypass Django's silent variable swallowing.
    """

    def __init__(self, template, *args, **kwargs):
        self.template = template

        super(TemplateErrorDict, self).__init__(*args, **kwargs)

    def __getitem__(self, key):
        if key not in self:
            raise TemplateErrorException(self.template % key)

        return super(TemplateErrorDict, self).__getitem__(key)


class TemplateErrorException(RuntimeError):
    silent_variable_failure = False


def is_lazy_translation(obj):
    # There's no public API to figure out the type of a "Promise"/"__proxy__"
    # object, so we look at whether the object has a string type in its set
    # of resultclasses. We do this so that we don't have to force the lazy
    # object as that may be expensive and we're likely working at import time.
    if not isinstance(obj, Promise):
        return False

    resultclasses = obj.__reduce__()[1][3:]
    return any(issubclass(x, six.string_types) for x in resultclasses)
