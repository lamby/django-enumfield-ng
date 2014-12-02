import inspect

from django.conf import settings
from django.utils.functional import memoize

from .enumeration import Enumeration

def enumfield_context(request):
    return {'enums': get_enums()}

def get_enums():
    result = {}

    for app in settings.INSTALLED_APPS:
        module = getattr(__import__(app, {}, {}, ('enums',)), 'enums', None)

        if module is None:
            continue

        for k, v in inspect.getmembers(module):
            if not inspect.isclass(v):
                continue

            if not issubclass(v, Enumeration) or v == Enumeration:
                continue

            result.setdefault(app.split('.')[-1], {})[k] = list(v)

    return result

get_enums = memoize(get_enums, {}, 0)
