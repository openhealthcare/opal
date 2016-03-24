"""
Unittests for opal.core.application
"""
from django.test import TestCase
from mock import patch, MagicMock

from opal.core import application

class OpalApplicationTestCase(TestCase):
    def setUp(self):
        class App(application.OpalApplication):
            flow_module = 'opal.tests.flows'

        self.app = App

    def test_get_menu_items(self):
        self.assertEqual([], application.OpalApplication.get_menu_items())



class GetAppTestCase(TestCase):
    @patch('opal.core.application.OpalApplication.__subclasses__')
    def test_get_app(self, subclasses):
        mock_app = MagicMock('Mock App')
        subclasses.return_value = [mock_app]
        self.assertEqual(mock_app, application.get_app())
