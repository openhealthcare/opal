"""
Unittests for opal.management.commands.load_lookup_lists
"""
import ffs
from mock import patch, MagicMock

from opal.core.test import OpalTestCase
from opal.tests.models import Dog

from opal.management.commands import load_lookup_lists as loader

class CommandTestCase(OpalTestCase):

    def test_init_sets_counter(self):
        c = loader.Command()
        self.assertEqual(0, c.num)
        self.assertEqual(0, c.created)
        self.assertEqual(0, c.synonyms)

    def test_from_path(self):
        pass


    # @patch('opal.management.commands.load_lookup_lists.os.path.isfile')
    # @patch('opal.management.commands.load_lookup_lists.ffs.Path')
    # def test_from_file(self, path, isfile):
    #     plugin = MagicMock()
    #     plugin.directory = MagicMock(return_value="somePlugin")
    #     plugin.__name__ = "somePlugin"
    #     isfile.return_value = True
    #     path.return_value.json_load.return_value = {}
    #     c = loader.Command()
    #     c.from_component(plugin)
    #     path.assert_any_call('somePlugin/data/lookuplists/lookuplists.json')

    # @patch('opal.management.commands.load_lookup_lists.os.path.isfile')
    # @patch('opal.management.commands.load_lookup_lists.ffs.Path')
    # def test_from_file_when_no_file(self, path, isfile):
    #     plugin = MagicMock()
    #     plugin.directory = MagicMock(return_value="somePlugin")
    #     plugin.__name__ = "somePlugin"
    #     isfile.return_value = False
    #     path.return_value.json_load.return_value = {}
    #     c = loader.Command()
    #     c.from_component(plugin)
    #     self.assertEqual(path.called, False)

    # @patch('opal.management.commands.load_lookup_lists.application.get_all_components')
    # @patch('opal.management.commands.load_lookup_lists.load_lookuplist')
    # @patch('opal.management.commands.load_lookup_lists.Command.from_component')
    # def test_handle(self, is_file, load_lookup_lists, get_all_components):
    #     plugin = MagicMock()
    #     plugin.directory = MagicMock(return_value="somePlugin")
    #     plugin.__name__ = "somePlugin"
    #     get_all_components.return_value = [plugin]
    #     is_file.return_value = {}
    #     load_lookup_lists.return_value = (1, 2, 3)

    #     cmd = loader.Command()
    #     cmd.stdout = MagicMock()
    #     cmd.handle()

    #     self.assertEqual(
    #         cmd.stdout.write.call_args[0][0],
    #         '\nFor somePlugin\nLoaded 1 lookup lists\n\n\nNew items report:\n\n\n2 new items 3 new synonyms'
    #     )
