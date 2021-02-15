"""
Unittests for opal.core.celery
"""
from unittest.mock import patch
from opal.core.test import OpalTestCase

from opal.core import celery


class DebugTaskTestCase(OpalTestCase):
    def test_with_runtests(self):
        with patch.object(celery.sys, 'stdout') as mock_stdout:
            celery.debug_task()
            mock_stdout.write.assert_called_with("Request: <Context: {'args': (), 'kwargs': {}}>\n")

    @patch("opal.core.celery.sys")
    @patch("opal.core.celery.Celery")
    @patch("opal.core.celery.os")
    def test_with_settings_module(self, os, Celery, sys):
        sys.argv = []
        os.environ = {'DJANGO_SETTINGS_MODULE': 'already_set'}
        celery.set_up()
        Celery.assert_called_once_with('opal')
        app = Celery.return_value
        app.config_from_object.assert_called_once_with(
            'django.conf:settings', namespace='CELERY'
        )
        app.autodiscover_tasks.assert_called_once_with()

    @patch("opal.core.celery.sys")
    @patch("opal.core.celery.Celery")
    @patch("opal.core.celery.os")
    @patch("opal.core.celery.commandline")
    def test_without_settings_module(self, commandline, os, Celery, sys):
        sys.argv = []
        os.environ = {}
        commandline.find_application_name.return_value = "my_fake_app"
        celery.set_up()
        Celery.assert_called_once_with('opal')
        app = Celery.return_value
        app.config_from_object.assert_called_once_with(
            'django.conf:settings', namespace='CELERY'
        )
        app.autodiscover_tasks.assert_called_once_with()
        self.assertEqual(
            os.environ, {"DJANGO_SETTINGS_MODULE": "my_fake_app.settings"}
        )
