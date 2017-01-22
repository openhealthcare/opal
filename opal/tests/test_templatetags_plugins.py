"""
Unittests for the opal.templatetags.plugins module
"""
from mock import patch, MagicMock

from opal.core import plugins
from opal.core.test import OpalTestCase
from opal.templatetags import plugins as opalplugins

class TestPlugin(plugins.OpalPlugin):
    javascripts = {
        'opal.test': ['js/test/notreal.js']
    }
    stylesheets = ['css/test/notreal.css']
    head_extra = ['notareal_template.html']
    menuitems =[ { 'display': 'test' } ]
    angular_module_deps = ['js/test.angular.mod.js']


class PluginJavascriptsTestCase(OpalTestCase):

    @patch('opal.templatetags.plugins.plugins.OpalPlugin.list')
    def test_plugin_javascripts(self, plugins):
        plugins.return_value = [TestPlugin]
        result = opalplugins.plugin_javascripts('opal.test')
        javascripts = [j for j in result['javascripts']()]
        expected = [
            'js/test/notreal.js'
        ]
        self.assertEqual(expected, javascripts)


class PluginStylesheetsTestCase(OpalTestCase):

    @patch('opal.templatetags.plugins.plugins.OpalPlugin.list')
    def test_plugin_stylesheets(self, plugins):
        plugins.return_value = [TestPlugin]
        css = list(opalplugins.plugin_stylesheets()['styles']())
        self.assertIn('css/test/notreal.css', css)


class PluginHeadExtraTestCase(OpalTestCase):

    @patch('opal.templatetags.plugins.plugins.OpalPlugin.list')
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

    @patch('opal.templatetags.plugins.plugins.OpalPlugin.list')
    def test_plugin_menuitems(self, plugins):
        plugins.return_value = [TestPlugin]
        menuitems = opalplugins.plugin_menuitems()['items']
        expected = [{'display': 'test'}]
        self.assertEqual(expected, menuitems)


class PluginAngularDepsTestCase(OpalTestCase):

    @patch('opal.templatetags.plugins.plugins.OpalPlugin.list')
    def test_plugin_angular_deps(self, plugins):
        plugins.return_value = [TestPlugin]
        deps = list(opalplugins.plugin_opal_angular_deps()['deps']())
        expected = ['js/test.angular.mod.js']
        self.assertEqual(expected, deps)

class PluginOPALAngularTrackingExcludeTestCase(OpalTestCase):

    @patch('opal.templatetags.plugins.plugins.OpalPlugin.list')
    def test_prefixes(self, plugins):
        plugins.return_value = [TestPlugin]
        expected_prefix = []
        expected_qs = [
            "/search",
            "/extract",
        ]
        context = opalplugins.plugin_opal_angular_tracking_exclude()
        prefixes = list(context['excluded_tracking_prefix'])
        qs = list(context['excluded_tracking_qs'])
        self.assertEqual(expected_prefix, prefixes)
        self.assertEqual(expected_qs, qs)
