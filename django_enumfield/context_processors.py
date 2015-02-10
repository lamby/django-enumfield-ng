import inspect

from django.conf import settings
from django.utils.functional import memoize

from .enum import Enum
from .utils import TemplateErrorDict

def enumfield_context(request):
    return {'enums': get_enums()}

def get_enums():
    result = TemplateErrorDict("Unknown app name %s")

    for app in settings.INSTALLED_APPS:
        module = getattr(__import__(app, {}, {}, ('enums',)), 'enums', None)

        if module is None:
            continue

        for _, x in inspect.getmembers(module):
            if not isinstance(x, Enum):
                continue

            app_name = app.split('.')[-1]

            result.setdefault(
                app_name,
                TemplateErrorDict("Unknown enum %%r in %r app" % app_name),
            )[x.name] = x

    return result

get_enums = memoize(get_enums, {}, 0)
