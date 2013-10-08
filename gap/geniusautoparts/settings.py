# Django settings for geniusautoparts project.
import os

from accounts import TEMPLATE_DIR as ACCOUNTS_TEMPLATE_DIR

from oscar import get_core_apps, OSCAR_MAIN_TEMPLATE_DIR
from oscar.defaults import *

location = lambda x: os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', x)

DEBUG = True
TEMPLATE_DEBUG = DEBUG


ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.4/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    location('static'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'zy1i9wzst!vqu$-n1+=k4c%h%)2p*j_ek3pbsj^@7@ppw)3txe'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',

    'oscar.apps.search.context_processors.search_form',
    'oscar.apps.promotions.context_processors.promotions',
    'oscar.apps.checkout.context_processors.checkout',
    'oscar.apps.customer.notifications.context_processors.notifications',
    'oscar.core.context_processors.metadata',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'oscar.apps.basket.middleware.BasketMiddleware',
)

ROOT_URLCONF = 'geniusautoparts.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'geniusautoparts.wsgi.application'

TEMPLATE_DIRS = (
    location('templates'),
    #os.path.join(OSCAR_PARENT_TEMPLATE_DIR, 'templates'),
    OSCAR_MAIN_TEMPLATE_DIR,
    ACCOUNTS_TEMPLATE_DIR,
)



USE_LESS = False

GRAPPELLI_ADMIN_TITLE = 'Genius'

INSTALLED_APPS = [
#    'admin_tools',
#    'admin_tools.theming',
#    'admin_tools.menu',
#    'admin_tools.dashboard',
    'grappelli',
    'django.contrib.humanize',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'django.contrib.admin',
    # 'django.contrib.admindocs',
    #'gap',
    'geniusautoparts',
    'accounts',
    'csvimport',
    'south',
    'compressor',
    'apps.checkout',
    'apps.dashboard.jobs',
    'paypal',
    'apps.pricelist',
    'apps.options',
    'apps.quotes',
    'apps.utils',
    'apps.globals',
    'apps.adminx',
]
INSTALLED_APPS = INSTALLED_APPS + get_core_apps(
    ['apps.order', 'apps.basket', 'apps.catalogue', 'apps.partner',])

ACCOUNTS_SOURCE_NAME = 'Main Account'
ACCOUNTS_REDEMPTIONS_NAME = 'Sales Account'
ACCOUNTS_LAPSED_NAME = 'Expired Account'

AUTHENTICATION_BACKENDS = (
    'oscar.apps.customer.auth_backends.Emailbackend',
    'django.contrib.auth.backends.ModelBackend',
)


EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/app-messages' # change this to a proper location

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
        },
    }

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s',
        },
        'simple': {
            'format': '[%(asctime)s] %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'error_file': {
            'level': 'INFO',
            'class': 'oscar.core.logging.handlers.EnvFileHandler',
            'filename': 'errors.log',
            'formatter': 'verbose'
        },
    },
    
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'error_file'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
LOG_ROOT = location('logs')


OSCAR_SHOP_NAME = 'Genius'
OSCAR_SHOP_TAGLINE = 'Test Shop'

OSCAR_INITIAL_ORDER_STATUS = 'Pending'
OSCAR_INITIAL_LINE_STATUS = 'Pending'
OSCAR_ORDER_STATUS_PIPELINE = {
    'Pending': ('Being processed', 'Cancelled',),
    'Being processed': ('Processed', 'Cancelled',),
    'Cancelled': (),
    }

AUTH_USER_EMAIL_UNIQUE = True


PAYPAL_API_USERNAME = 'sinezub-facilitator_api1.yandex.ru'
PAYPAL_API_PASSWORD = '1369339401'
PAYPAL_API_SIGNATURE = 'AX8GCu0CvjNpRud8qe-xAmm7JGjlA-jk1t4X3azsbXycax.HvbLdO-mu'
PAYPAL_CALLBACK_TIMEOUT = 30

OSCAR_DASHBOARD_NAVIGATION[2] = {
        'label': 'Fulfilment',
        'icon': 'icon-shopping-cart',
        'children': [
            {
                'label': 'Order management',
                'url_name': 'dashboard:order-list',
            },
            {
                'label': 'Jobs management',
                'url_name': 'job-list',
            },
            {
                'label': 'Statistics',
                'url_name': 'dashboard:order-stats',
            },
            {
                'label': 'Partners',
                'url_name': 'dashboard:partner-list',
            },
        ]
    }


OSCAR_DASHBOARD_NAVIGATION += [
    {
        'label': 'Pricelist',
        'icon': 'icon-list',
        'children': [
            {
                'label': 'Import',
                'url_name': 'apps.pricelist.views.import_pricelist',
            },
            {
                'label': 'List',
                'url_name': 'apps.pricelist.views.list',
            },

         ]
    },
]
GRAPPELLI_AUTOCOMPLETE_SEARCH_FIELDS = {
    "apps.options": {
        "OptionChoice": ("code__icontains",)
    }
}
MISSING_OPTIONCHOICE_THUMB_URL = STATIC_URL + 'options/img/missing-choice-thumbnail.png'
OPTIONCHOICE_CUSTOMSIZE = ('size', 'custom')
TRADE_GROUP_NAME = 'Trade'
MAX_SAVED_QUOTES = 15
OPTION_ITEMSPERPACK = 'items_per_pack'

# TODO: Modify this
OSCAR_MISSING_IMAGE_URL = STATIC_URL + 'options/img/missing-choice-thumbnail.png'

from local_settings import *
