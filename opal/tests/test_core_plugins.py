"""
Unittests for opal.core.plugins
"""
import warnings

from mock import patch

from opal.core.test import OpalTestCase

from opal.core import plugins


class OpalPluginTestCase(OpalTestCase):
    def setUp(self):
        class TestPlugin1(plugins.OpalPlugin):
            javascripts = {
                'opal.test': ['js/test/notreal.js']
            }
            stylesheets = ['css/test/notreal.css']
            head_extra = ['notareal_template.html']
            menuitems =[ { 'display': 'test' } ]
            angular_module_deps = ['js/test.angular.mod.js']

        class TestPlugin2(plugins.OpalPlugin):
            stylesheets = ['css/test/notreal.scss']

        self.plugin1 = TestPlugin1
        self.plugin2 = TestPlugin2

    @patch("opal.core.plugins.inspect.getfile")
    def test_directory(self, getfile):
        getfile.return_value = "/"
        plugin = list(plugins.OpalPlugin.list())[0]
        self.assertEqual(plugin.directory(), "/")

    def test_get_css_styles(self):
        self.assertEqual(
            self.plugin1.get_styles(),
             ['css/test/notreal.css']
        )

    def test_get_javascripts(self):
        self.assertEqual(
            self.plugin1.get_javascripts(),
             {'opal.test': ['js/test/notreal.js']}
        )

class RegisterPluginsTestCase(OpalTestCase):

    def test_register_warns(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            plugins.register(None)
            assert len(w) == 1
            assert issubclass(w[-1].category, DeprecationWarning)
            assert "no longer required" in str(w[-1].message)


class PluginsPluginsTestCase(OpalTestCase):
    def test_plugins_warns(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            plugins.plugins()
            assert len(w) == 1
            assert issubclass(w[-1].category, DeprecationWarning)
            assert "slated for removal" in str(w[-1].message)
