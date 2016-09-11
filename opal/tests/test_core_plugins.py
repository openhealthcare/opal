"""
Unittests for opal.core.plugins
"""
from mock import patch
from opal.core.test import OpalTestCase
from opal.core import plugins
from opal.tests.test_templatetags_plugins import TestPlugin


class OpalPluginTestCase(OpalTestCase):
    def test_flows(self):
        self.assertEqual({}, plugins.OpalPlugin().flows())

    @patch("opal.core.plugins.inspect.getfile")
    def test_directory(self, getfile):
        getfile.return_value = "/"
        plugin = list(plugins.plugins())[0]
        self.assertEqual(plugin.directory(), "/")
