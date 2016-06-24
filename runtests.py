"""
Standalone test runner for OPAL plugin
"""
import os
import sys

from django.conf import settings

settings.configure(DEBUG=True,
                   DATABASES={
                       'default': {
                           'ENGINE': 'django.db.backends.sqlite3',
                       }
                   },
                   OPAL_OPTIONS_MODULE = 'opal.tests.dummy_options_module',
                   ROOT_URLCONF='opal.urls',
                   USE_TZ=True,
                   OPAL_EXTRA_APPLICATION='',
                   DATE_FORMAT='d/m/Y',
                   DATE_INPUT_FORMATS=['%d/%m/%Y'],
                   DATETIME_FORMAT='d/m/Y H:i:s',
                   DATETIME_INPUT_FORMATS=['%d/%m/%Y %H:%M:%S'],
                   STATIC_URL='/assets/',
                   COMPRESS_ROOT='/tmp/',
                   TIME_ZONE='UTC',
                   OPAL_BRAND_NAME = 'opal',
                   INTEGRATING=False,
                   DEFAULT_DOMAIN='localhost',
                   MIDDLEWARE_CLASSES = (
                       'django.middleware.common.CommonMiddleware',
                       'django.contrib.sessions.middleware.SessionMiddleware',
                       'opal.middleware.AngularCSRFRename',
                       'django.middleware.csrf.CsrfViewMiddleware',
                       'django.contrib.auth.middleware.AuthenticationMiddleware',
                       'django.contrib.messages.middleware.MessageMiddleware',
                       'opal.middleware.DjangoReversionWorkaround',
                       'reversion.middleware.RevisionMiddleware',
                       'axes.middleware.FailedLoginMiddleware',
                   ),
                   INSTALLED_APPS=('django.contrib.auth',
                                   'django.contrib.contenttypes',
                                   'django.contrib.staticfiles',
                                   'django.contrib.sessions',
                                   'django.contrib.admin',
                                   'reversion',
                                   'compressor',
                                   'djcelery',
                                   'opal',
                                   'opal.core.search',
                                   'opal.tests'
                               ),
                   MIGRATION_MODULES={
                       'opal': 'opal.nomigrations'
                   },
                   TEMPLATE_LOADERS = (
                       ('django.template.loaders.cached.Loader', (
                           'django.template.loaders.filesystem.Loader',
                           'django.template.loaders.app_directories.Loader',
                           )),
                   ),
                   CELERY_ALWAYS_EAGER=True
)

from opal.tests import dummy_options_module
from opal.tests import dummy_opal_application


import django
django.setup()
from opal.core import celery
celery.app.config_from_object('django.conf:settings')


from django.test.runner import DiscoverRunner
test_runner = DiscoverRunner(verbosity=1)
if len(sys.argv) == 2:
    failures = test_runner.run_tests([sys.argv[-1], ])
else:
    failures = test_runner.run_tests(['opal', ])
    if failures:
        sys.exit(failures)
