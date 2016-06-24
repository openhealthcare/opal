"""
Unittests for opal.management.commands.load_lookup_lists
"""
from mock import patch, MagicMock

from opal.core.test import OpalTestCase
from opal.tests.models import Dog

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

    @patch('opal.management.commands.load_lookup_lists.ffs.Path')
    def test_handle_empty_file(self, path):
        path.return_value.json_load.return_value = {}
        c = loader.Command()
        with patch.object(c.stdout, 'write'): # Quiet down our test running
            c.handle(filename='this.json')
        path.assert_called_with('this.json')

    @patch('opal.management.commands.load_lookup_lists.ffs.Path')
    def test_handle_load_colour(self, path):
        path.return_value.json_load.return_value = {
            'dog': [{'name': 'terrier', 'synonyms': ['yorkshire terrier']}]
        }
        c = loader.Command()
        with patch.object(c.stdout, 'write'): # Quiet down our test running
            c.handle(filename='this.json')
            self.assertEqual(1, Dog.objects.filter(name='terrier').count())
