"""
Unittests for opal.core.plugins
"""
import os
import copy

from unittest.mock import patch

from opal.core.test import OpalTestCase
from opal.core import menus
from opal.utils import AbstractBase

from opal.core import plugins


class OpalPluginTestCase(OpalTestCase):
    def setUp(self):
        class TestPlugin1(plugins.OpalPlugin):
            javascripts = ['js/test/notreal.js']
            stylesheets = ['css/test/notreal.css']
            head_extra = ['notareal_template.html']
            menuitems = [menus.MenuItem(display='test') ]
            angular_module_deps = ['js/test.angular.mod.js']

        class TestPlugin2(plugins.OpalPlugin):
            stylesheets = ['css/test/notreal.scss']

        self.plugin1 = TestPlugin1
        self.plugin2 = TestPlugin2

    def test_get_urls(self):
        self.assertEqual([], self.plugin1.get_urls())

    def test_get_urls_side_effects(self):
        urls = self.plugin1.get_urls()
        urls_orig = copy.copy(urls)
        urls.append('/some/url')
        self.assertEqual(urls_orig, self.plugin1.get_urls())

    def test_get_apis(self):
        self.assertEqual([], self.plugin1.get_apis())

    def test_get_apis_side_effects(self):
        apis = self.plugin1.get_apis()
        apis_orig = copy.copy(apis)
        apis.append('my api')
        self.assertEqual(apis_orig, self.plugin1.get_apis())

    @patch("opal.core.plugins.inspect.getfile")
    def test_directory(self, getfile):
        getfile.return_value = "/"
        plugin = list(plugins.OpalPlugin.list())[0]
        self.assertEqual(plugin.directory(), os.path.abspath(os.sep))

    def test_get_css_styles(self):
        self.assertEqual(
            self.plugin1.get_styles(),
             ['css/test/notreal.css']
        )

    def test_get_styles_side_effects(self):
        css = self.plugin1.get_styles()
        css_orig = copy.copy(css)
        css.append('IE6.polyfills.css')
        self.assertEqual(css_orig, self.plugin1.get_styles())

    def test_get_javascripts(self):
        self.assertEqual(
            self.plugin1.get_javascripts(),
            ['js/test/notreal.js']
        )

    def test_get_javascripts_side_effects(self):
        js = self.plugin1.get_javascripts()
        js_orig = copy.copy(js)
        js.append('icanhazcheezburgerify.js')
        self.assertEqual(js_orig, self.plugin1.get_javascripts())

    def test_get_menu_items(self):
        class MenuItemIncluded(menus.MenuItem):
            pass

        class MenuItemNotIncluded(menus.MenuItem):
            def for_user(self, user):
                return False

        menu_item_included = MenuItemIncluded()
        menu_item_not_included = MenuItemNotIncluded()

        class TestPlugin(plugins.OpalPlugin, AbstractBase):
                menuitems = [
                    menu_item_included, menu_item_not_included
                ]

        self.assertEqual(
            [menu_item_included],
            list(TestPlugin.get_menu_items())
        )