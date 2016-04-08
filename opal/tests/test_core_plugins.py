"""
Unittests for opal.core.plugins
"""
from opal.core.test import OpalTestCase

from opal.core import plugins

class OpalPluginTestCase(OpalTestCase):

    def test_flows(self):
        self.assertEqual({}, plugins.OpalPlugin().flows())
