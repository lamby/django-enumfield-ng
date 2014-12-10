from django.http import Http404

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
