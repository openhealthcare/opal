"""
Unittests for the opal.templatetags.opalplugins module
"""
from mock import patch, MagicMock

from opal.core import plugins
from opal.core.test import OpalTestCase
from opal.templatetags import opalplugins

class TestPlugin(plugins.OpalPlugin):
    javascripts = {
        'opal.test': ['js/test/notreal.js']
    }
    stylesheets = ['css/test/notreal.css']
    head_extra = ['notareal_template.html']
    menuitems =[ { 'display': 'test' } ]
    angular_module_deps = ['js/test.angular.mod.js']


class PluginJavascriptsTestCase(OpalTestCase):

    @patch('opal.templatetags.opalplugins.plugins.plugins')
    def test_plugin_javascripts(self, plugins):
        plugins.return_value = [TestPlugin]
        result = opalplugins.plugin_javascripts('opal.test')
        javascripts = [j for j in result['javascripts']()]
        expected = [
            'js/test/notreal.js'
        ]
        self.assertEqual(expected, javascripts)


class PluginStylesheetsTestCase(OpalTestCase):

    @patch('opal.templatetags.opalplugins.plugins.plugins')
    def test_plugin_stylesheets(self, plugins):
        plugins.return_value = [TestPlugin]
        css = list(opalplugins.plugin_stylesheets()['styles']())
        self.assertIn('css/test/notreal.css', css)


class PluginHeadExtraTestCase(OpalTestCase):

    @patch('opal.templatetags.opalplugins.plugins.plugins')
    def test_plugin_head_extra(self, plugins):
        plugins.return_value = [TestPlugin]
        context = opalplugins.plugin_head_extra({})
        templates = list(context['head_extra']())
        self.assertEqual(['notareal_template.html'], templates)


class MenuItemOrderingTest(OpalTestCase):
    def test_with_fields_some_with_index(self):
        td = [
            dict(display="a", index=10),
            dict(display="b", index=10),
            dict(display="c", index=9),
            dict(display="d"),
        ]
        self.assertEqual(opalplugins.sort_menu_items(td), [td[2], td[0], td[1], td[3]])


class PluginMenuitemsTestCase(OpalTestCase):

    @patch('opal.templatetags.opalplugins.plugins.plugins')
    def test_plugin_menuitems(self, plugins):
        plugins.return_value = [TestPlugin]
        menuitems = opalplugins.plugin_menuitems()['items']
        expected = [{'display': 'test'}]
        self.assertEqual(expected, menuitems)


class ApplicationMenuitemsTestCase(OpalTestCase):

    @patch('opal.templatetags.opalplugins.application.get_app')
    def test_application_menuitems(self, get_app):
        mock_app = MagicMock(name='Application')
        mock_app.menuitems = [{'display': 'test'}]
        get_app.return_value = mock_app
        result = list(opalplugins.application_menuitems()['items']())
        expected = [{'display': 'test'}]
        self.assertEqual(expected, result)


class PluginAngularDeps(OpalTestCase):

    @patch('opal.templatetags.opalplugins.plugins.plugins')
    def test_plugin_angular_deps(self, plugins):
        plugins.return_value = [TestPlugin]
        deps = list(opalplugins.plugin_opal_angular_deps()['deps']())
        expected = ['js/test.angular.mod.js']
        self.assertEqual(expected, deps)
