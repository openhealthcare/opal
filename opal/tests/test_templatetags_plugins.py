"""
Unittests for the opal.templatetags.plugins module
"""
import warnings

from mock import patch

from opal.core import plugins
from opal.core.test import OpalTestCase
from opal.templatetags import plugins as opalplugins


@patch('opal.templatetags.plugins.plugins.OpalPlugin.list')
class PluginTestCase(OpalTestCase):
    def setUp(self):
        class TestPlugin1(plugins.OpalPlugin):
            javascripts = {
                'opal.test': ['js/test/notreal.js']
            }
            stylesheets = ['css/test/notreal.css']
            head_extra = ['notareal_template.html']
            menuitems = [{'display': 'test'}]
            angular_module_deps = ['js/test.angular.mod.js']

        class TestPlugin2(plugins.OpalPlugin):
            stylesheets = ['css/test/notreal.scss']
        self.plugin1 = TestPlugin1
        self.plugin2 = TestPlugin2

    def test_plugin_javascripts(self, plugins):
        plugins.return_value = [self.plugin1]
        result = opalplugins.plugin_javascripts('opal.test')
        javascripts = [j for j in result['javascripts']()]
        expected = [
            'js/test/notreal.js'
        ]
        self.assertEqual(expected, javascripts)

    def test_plugin_css_stylesheets(self, plugins):
        plugins.return_value = [self.plugin1]
        css = list(opalplugins.plugin_stylesheets()['styles']())
        expected = [('css/test/notreal.css', 'text/css')]
        self.assertEqual(css, expected)

    def test_plugin_scss_stylesheets(self, plugins):
        plugins.return_value = [self.plugin2]
        css = list(opalplugins.plugin_stylesheets()['styles']())
        expected = [('css/test/notreal.scss', 'text/x-scss')]
        self.assertEqual(css, expected)

    def test_plugin_head_extra(self, plugins):
        plugins.return_value = [self.plugin1]
        context = opalplugins.plugin_head_extra({})
        templates = list(context['head_extra']())
        self.assertEqual(['notareal_template.html'], templates)

    def test_plugin_angular_deps(self, plugins):
        plugins.return_value = [self.plugin1]
        deps = list(opalplugins.plugin_opal_angular_deps()['deps']())
        expected = ['js/test.angular.mod.js']
        self.assertEqual(expected, deps)

    def test_prefixes(self, plugins):
        plugins.return_value = [self.plugin1]
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

    def test_plugin_menuitems(self, plugins):
        with warnings.catch_warnings(record=True):
            plugins.return_value = [self.plugin1]
            menuitems = opalplugins.plugin_menuitems()['items']
            expected = [{'display': 'test'}]
            self.assertEqual(expected, menuitems)


class MenuItemOrderingTest(OpalTestCase):
    def test_with_fields_some_with_index(self):
        td = [
            dict(display="a", index=10),
            dict(display="b", index=10),
            dict(display="c", index=9),
            dict(display="d"),
        ]
        self.assertEqual(opalplugins.sort_menu_items(td), [td[2], td[0], td[1], td[3]])
