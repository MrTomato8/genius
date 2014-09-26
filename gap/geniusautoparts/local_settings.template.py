from .settings import rel

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': rel('..', '..', 'db', 'geniusautoparts.db'),
    }
}