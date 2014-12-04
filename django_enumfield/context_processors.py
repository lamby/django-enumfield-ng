import inspect

from django.conf import settings
from django.utils.functional import memoize

from .utils import TemplateErrorDict
from .enumeration import Enumeration

def enumfield_context(request):
    return {'enums': get_enums()}

def get_enums():
    result = TemplateErrorDict("Unknown app name %s")

    for app in settings.INSTALLED_APPS:
        module = getattr(__import__(app, {}, {}, ('enums',)), 'enums', None)

        if module is None:
            continue

        for k, v in inspect.getmembers(module):
            if not inspect.isclass(v):
                continue

            if not issubclass(v, Enumeration) or v == Enumeration:
                continue

            app_name = app.split('.')[-1]

            result.setdefault(
                app_name,
                TemplateErrorDict("Unknown enum %%r in %r app" % app_name),
            )[k] = list(v)

    return result

get_enums = memoize(get_enums, {}, 0)
