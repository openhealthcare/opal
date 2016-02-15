"""
Unittests for opal.management.commands.load_lookup_lists
"""
from mock import patch

from opal.core.test import OpalTestCase

from opal.management.commands import load_lookup_lists as loader

class CommandTestCase(OpalTestCase):
    def test_init(self):
        c = loader.Command()
        self.assertEqual(0, c.items_created)
        self.assertEqual(0, c.synonyms_created)

    def test_handle_no_lookuplist(self):
        c = loader.Command()
        with self.assertRaises(ValueError):
            c.handle()
