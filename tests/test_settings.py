SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    'tests',
    'tests.app',
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django_enumfield.context_processors.enumfield_context',
            ],
        },
    },
]
SILENCED_SYSTEM_CHECKS = [
    '1_7.W001',
]
ROOT_URLCONF = 'tests.urls'
