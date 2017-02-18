"""
Unittests for opal.core.plugins
"""
import warnings

from mock import patch

from opal.core.test import OpalTestCase

from opal.tests.test_templatetags_plugins import TestPlugin
from opal.core import plugins

class OpalPluginTestCase(OpalTestCase):

    @patch("opal.core.plugins.inspect.getfile")
    def test_directory(self, getfile):
        getfile.return_value = "/"
        plugin = list(plugins.OpalPlugin.list())[0]
        self.assertEqual(plugin.directory(), "/")


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
