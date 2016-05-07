"""
Unittests for the opal.templatetags.application module
"""
from mock import patch, MagicMock

from opal.core.test import OpalTestCase
from opal.templatetags import application

class ApplicationMenuitemsTestCase(OpalTestCase):

    @patch('opal.templatetags.application.application.get_app')
    def test_application_menuitems(self, get_app):
        mock_app = MagicMock(name='Application')
        mock_app.menuitems = [{'display': 'test'}]
        get_app.return_value = mock_app
        result = list(application.application_menuitems()['items']())
        expected = [{'display': 'test'}]
        self.assertEqual(expected, result)


class CoreJavascriptTestCase(OpalTestCase):

    @patch('opal.templatetags.application.application.get_app')
    def test_core_javascripts(self, get_app):
        mock_app = MagicMock(name='Application')
        mock_app.core_javascripts = {'opal': ['test.js']}
        get_app.return_value = mock_app

        result = list(application.core_javascripts('opal')['javascripts']())

        self.assertEqual(['test.js'], result)


class ApplicationJavascriptTestCase(OpalTestCase):

    @patch('opal.templatetags.application.application.get_app')
    def test_core_javascripts(self, get_app):
        mock_app = MagicMock(name='Application')
        mock_app.javascripts = ['test.js']
        get_app.return_value = mock_app

        result = list(application.application_javascripts()['javascripts']())

        self.assertEqual(['test.js'], result)


class ApplicationStylesTestCase(OpalTestCase):

    @patch('opal.templatetags.application.application.get_app')
    def test_core_styles(self, get_app):
        mock_app = MagicMock(name='Application')
        mock_app.styles = ['test.css']
        get_app.return_value = mock_app

        result = list(application.application_stylesheets()['styles']())

        self.assertEqual(['test.css'], result)
