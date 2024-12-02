"""
Django settings for slicerepublic project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@86!7k_=^vf_ey1ig-r!&5m!mos7oxn6*7t1xcln&ccx=d-vxh'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',

    'bookings.bookings_core',
    'bookings.bookings_api',
    'bookings.bookings_web',

    'studios.studios_web',

    'classes',
    'scheduler',
    'staff',
    'venues',
    'slice',
    'services',
    'fcm',
    'ratings',
    'notifications',
    'rest_framework',

    'widget_tweaks',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'formatter': 'verbose',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'slicerepublic.log',
            'encoding': 'utf8',
            'when': 'd',
            'interval': 14,
            'backupCount': 6,
        }

    },
    'loggers': {
        # 'django': {
        #     'handlers':['file'],
        #     'propagate': True,
        #     'level':'DEBUG',
        # },
        'accounts': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'bookings': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'mind_body_service': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'mind_body_online': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'services': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'venues': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'ratings': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'notifications': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'fcm': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}

# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': {
#         'rest_framework.authentication.BasicAuthentication',
#         'rest_framework.authentication.SessionAuthentication',
#         'rest_framework.authentication.TokenAuthentication',
#     }
# }

from datetime import timedelta
from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'sync-mbo-resources': {
        'task': 'scheduler.tasks.sync_mbo_resources',
        'schedule': crontab(hour='*', minute=0),
    },
    'handle_unpaid_bookings': {
        'task': 'scheduler.tasks.handle_unpaid_bookings',
        'schedule': crontab(hour=0, minute=0),
    },
    'cancel_test_user_bookings': {
        'task': 'bookings.bookings_core.tasks.cancel_test_user_bookings',
        'schedule': crontab(hour='*', minute=0),
    },
    'check_studio_integration': {
        'task': 'venues.tasks.check_studio_integration',
        'schedule': crontab(hour=0, minute=0),
    }
}

CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = 'Europe/London'

BROKER_URL = "redis://localhost:6379/0"
BROKER_BACKEND = "redis"
REDIS_LOCK_TIMEOUT = 30 * 60  # 30 minutes
CLIENT_BOOKINGS_SYNC_TIMEOUT = 5 * 60  # 5 minutes
STUDIO_SERVICES_SYNC_TIMEOUT = 60 * 60  # 1 hour
CLIENT_SERVICES_SYNC_TIMEOUT = 60 * 60 * 24 * 7

NOTIFY_USERS_SYNC_TIMEOUT = 60 * 60 * 24 * 7

CLIENT_SERVICES_TIMEDELTA_INTERVAL = 30 * 6

MBO_SOURCE = 'Slice'
MBO_KEY = 'B3z1D4SFdC/F9Ewbtx1g8nfRPGE='
MBO_STAFF_USERNAME = '_Slice'
MBO_STAFF_PASSWORD = 'B3z1D4SFdC/F9Ewbtx1g8nfRPGE='
MBO_PAGE_SIZE = 100

GEO_SIGN_IN_RADIUS = 100

AUTH_USER_MODEL = 'accounts.User'

ROOT_URLCONF = 'slicerepublic.urls'

WSGI_APPLICATION = 'slicerepublic.wsgi.application'

EXTERNAL_CREDIT_LIMIT = 5

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME':  'checkout_release',  # change the database name
        'USER': 'root',  # change the user name
        'PASSWORD': 'password',  # change the password
        'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
        'CONN_MAX_AGE': 600,
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 300,
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

EMAIL_HOST = 'smtp.mandrillapp.com'
EMAIL_HOST_USER = 'hello@slicerepublic.com'
EMAIL_HOST_PASSWORD = 'dxpLANUGNMQ5-l-NnVFIFA'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_SLICE_REPUBLIC_FROM = 'Fitopia <hello@fitopia.co.uk>'

FITOPIA_ADMIN_EMAIL_ADDRESSES = ['155indiran@gmail.com', 'hamish.barclay@slicefitness.com', 'sp.fitopia@gmail.com ']

# EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
# EMAIL_FILE_PATH = '/tmp/app-emails'

TFL_APP_ID = 'ad3be72a'
TFL_APP_KEY = '5b3509f7e8476bb39899287b9ae23b4b'

CREDIT_CARD_CHECKOUT_TEST = False

SIGNUP_VERIFICATION_HOST_NAME = ''
FCM_API_KEY = "AIzaSyCZZBYVsJmJWUymnzhmi0N87mNDVe9ifbc"

# CELERY STUFF
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 1209600}

SEARCH_PAGE_LIMIT = 25
DEFAULT_PAGE_COUNT = 20
