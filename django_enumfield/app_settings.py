from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

TEMPLATE = "ENUMFIELD_%s"


class NOT_PROVIDED:  # noqa
    pass


def setting(suffix, default=NOT_PROVIDED):
    # Lazily get settings from ``django.conf.settings`` instance so that the
    # @override_settings works.
    @property
    def fn(self):
        key = TEMPLATE % suffix

        try:
            if default is NOT_PROVIDED:
                return getattr(settings, key)
        except AttributeError:
            raise ImproperlyConfigured("Missing required setting: {}".format(key))

        return getattr(settings, key, default)

    return fn


class AppSettings:
    EXPLICIT_SLUGS = setting("EXPLICIT_SLUGS", default=False)


app_settings = AppSettings()
