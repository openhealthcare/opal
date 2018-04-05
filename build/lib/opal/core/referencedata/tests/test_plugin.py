"""
Unittests for the opal.core.referencedata plugin
"""
from opal.core.test import OpalTestCase
from opal.core import plugins

from opal.core.referencedata import plugin


class PluginTestCase(OpalTestCase):

    def test_plugin_instance_exists(self):
        instances = []
        for d in vars(plugin).values():
            try:
                if issubclass(d, plugins.OpalPlugin):
                    instances.append(d)
            except TypeError:
                continue  # Can't call issubclass on not a class, don't care.

        self.assertEqual(1, len(instances))
