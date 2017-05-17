import inspect

from django.apps import apps
from django.utils.lru_cache import lru_cache

from .enum import Enum
from .utils import TemplateErrorDict

def enumfield_context(request):
    return {'enums': get_enums()}

@lru_cache()
def get_enums():
    result = TemplateErrorDict("Unknown app name %s")

    for app_config in apps.get_app_configs():
        module = getattr(__import__(app_config.name, {}, {}, ('enums',)), 'enums', None)

        if module is None:
            continue

        for _, x in inspect.getmembers(module):
            if not isinstance(x, Enum):
                continue

            app_name = app_config.name.split('.')[-1]

            result.setdefault(
                app_name,
                TemplateErrorDict("Unknown enum %%r in %r app" % app_name),
            )[x.name] = x

    return result
