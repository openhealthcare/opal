"""
Unittests for the opal.templatetags.application module
"""
from mock import patch, MagicMock

from opal.core import plugins
from opal.core.test import OpalTestCase
from opal.templatetags import application

class TestPlugin(plugins.OpalPlugin):
    actions = ['pluginaction.html']

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
        mock_app.get_core_javascripts.return_value = ['test.js']
        get_app.return_value = mock_app

        result = list(application.core_javascripts('opal')['javascripts']())

        self.assertEqual(['test.js'], result)
        mock_app.get_core_javascripts.assert_called_with('opal')


class ApplicationJavascriptTestCase(OpalTestCase):

    @patch('opal.templatetags.application.application.get_app')
    def test_core_javascripts(self, get_app):
        mock_app = MagicMock(name='Application')
        mock_app.get_javascripts.return_value = ['test.js']
        get_app.return_value = mock_app

        result = list(application.application_javascripts()['javascripts']())

        self.assertEqual(['test.js'], result)
        mock_app.get_javascripts.assert_called_with()


class ApplicationStylesTestCase(OpalTestCase):

    @patch('opal.templatetags.application.application.get_app')
    def test_core_styles(self, get_app):
        mock_app = MagicMock(name='Application')
        mock_app.get_styles.return_value = ['test.css']
        get_app.return_value = mock_app

        result = list(application.application_stylesheets()['styles']())

        self.assertEqual(['test.css'], result)
        mock_app.get_styles.assert_called_with()


class ApplicatoinActionsTestCase(OpalTestCase):

    @patch('opal.templatetags.application.plugins.plugins')
    @patch('opal.templatetags.application.application.get_app')
    def test_application_actions(self, get_app, get_plugins):
        mock_app = MagicMock(name='Application')
        mock_app.actions = ['action1.html']
        get_app.return_value = mock_app
        get_plugins.return_value = [TestPlugin]

        result = list(application.application_actions()['actions']())
        self.assertEqual(['action1.html', 'pluginaction.html'], result)
