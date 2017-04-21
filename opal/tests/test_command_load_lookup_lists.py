"""
Unittests for opal.management.commands.load_lookup_lists
"""
import ffs
from mock import patch, MagicMock

from opal.core import application
from opal.core.test import OpalTestCase
from opal.tests.models import Dog

from opal.management.commands import load_lookup_lists as loader

class CommandTestCase(OpalTestCase):

    def test_init_sets_counter(self):
        c = loader.Command()
        self.assertEqual(0, c.num)
        self.assertEqual(0, c.created)
        self.assertEqual(0, c.synonyms)

    def test_from_path_does_not_exist(self):
        mock_path = MagicMock()
        if hasattr(mock_path, '__bool__'):
            mock_path.__bool__.return_value = False
        else:
            mock_path.__nonzero__.return_value = False
        c = loader.Command()
        self.assertEqual({}, c.from_path(mock_path))

    def test_from_path_json(self):
        mock_path = MagicMock()
        if hasattr(mock_path, '__bool__'):
            mock_path.__bool__.return_value = True
        else:
            mock_path.__nonzero__.return_value = True
        mock_path.json_load.return_value = {'hai': 'world'}
        c = loader.Command()
        self.assertEqual({'hai': 'world'}, c.from_path(mock_path))

    @patch('ffs.Path')
    def test_from_component(self, path):
        c = loader.Command()
        c.from_component(application.get_app())
        calls = [c[0][0] for c in path.call_args_list]
        expected = [
            'data/lookuplists/lookuplists.json',
            'data/lookuplists/drug.json',
            'data/lookuplists/condition.json'
        ]
        for e in expected:
            self.assertTrue(len([c for c in calls if c.endswith(e)]) == 1)

    def test_handle(self):
        c = loader.Command()
        with patch.object(c, 'stdout') as stdout:
            c.handle()
            stdout.write.assert_any_call(
                '\nFor SearchPlugin\nLoaded 0 lookup lists\n\n\nNew items report:\n\n\n0 new items 0 new synonyms'
            )



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
