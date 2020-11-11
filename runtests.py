"""
Standalone test runner for Opal
"""
import os
import sys

from django.conf import settings

PROJECT_PATH = os.path.join(
    os.path.realpath(os.path.dirname(__file__)), "opal"
)

test_settings_config = dict(
    DEBUG=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
        }
    },
    PROJECT_PATH=PROJECT_PATH,
    ROOT_URLCONF='opal.urls',
    USE_TZ=True,
    OPAL_EXTRA_APPLICATION='',
    DATE_FORMAT='d/m/Y',
    DATE_INPUT_FORMATS=['%d/%m/%Y'],
    DATETIME_FORMAT='d/m/Y H:i:s',
    DATETIME_INPUT_FORMATS=['%d/%m/%Y %H:%M:%S'],
    TIME_FORMAT = "H:i:s",
    STATIC_URL='/assets/',
    COMPRESS_ROOT='/tmp/',
    TIME_ZONE='UTC',
    OPAL_BRAND_NAME = 'opal',
    INTEGRATING=False,
    DEFAULT_DOMAIN='localhost',
    MIDDLEWARE=(
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'opal.middleware.AngularCSRFRename',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'opal.middleware.DjangoReversionWorkaround',
        'reversion.middleware.RevisionMiddleware'
    ),
    INSTALLED_APPS=(
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.staticfiles',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.admin',
        'reversion',
        'compressor',
        'axes',
        'djcelery',
        'opal',
        'opal.tests',
        'opal.core.search',
        'opal.core.pathway.tests.pathway_test',
        'opal.core.pathway',
    ),
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.contrib.auth.context_processors.auth',
                    'django.template.context_processors.debug',
                    'django.template.context_processors.i18n',
                    'django.template.context_processors.media',
                    'django.template.context_processors.request',
                    'django.template.context_processors.static',
                    'django.template.context_processors.tz',
                    'django.contrib.messages.context_processors.messages',
                    'opal.context_processors.settings',
                    'opal.context_processors.models'
                ],
                # ... some options here ...
            },
        },
    ],
    CELERY_ALWAYS_EAGER=True,
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'opal.core.log.ConfidentialEmailer'
            },
        },
        'loggers': {
            'django': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': True,
            },
        }
    },
    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.TokenAuthentication',
            'rest_framework.authentication.SessionAuthentication',
        )
    }
)

if 'TRAVIS' in os.environ:
    test_settings_config["DATABASES"] = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'travis_ci_test',
            'USER': 'postgres',
            'PASSWORD': '',
            'HOST': 'localhost',
        }
    }

settings.configure(**test_settings_config)

from opal.tests import dummy_opal_application  # NOQA


import django
django.setup()
from opal.core import celery
celery.app.config_from_object('django.conf:settings')

try:
    sys.argv.remove('--failfast')
    failfast = True
except ValueError:
    failfast = False

from django.test.runner import DiscoverRunner
test_runner = DiscoverRunner(verbosity=1, failfast=failfast)
if len(sys.argv) == 2:
    failures = test_runner.run_tests([sys.argv[-1], ])
else:
    failures = test_runner.run_tests(['opal', ])
    if failures:
        sys.exit(bool(failures))
