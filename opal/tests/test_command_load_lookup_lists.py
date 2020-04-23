"""
Unittests for opal.management.commands.load_lookup_lists
"""
import os
from unittest.mock import patch, MagicMock

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

    def test_add_arguments(self):
        c = loader.Command()
        parser = MagicMock()
        c.add_arguments(parser)
        parser.add_argument.assert_called_once_with(
            '--file',
            help="Specify import file",
            dest="filename"
        )

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
            os.path.join('data', 'lookuplists', 'lookuplists.json'),
            os.path.join('data', 'lookuplists', 'drug.json'),
            os.path.join('data', 'lookuplists', 'condition.json'),
        ]
        for e in expected:
            self.assertTrue(len([c for c in calls if c.endswith(e)]) == 1)

    def test_handle_explicit_filename(self):
        c = loader.Command()
        with patch.object(c, 'stdout') as stdout:
            c.handle(filename='this.json')
            stdout.write.assert_any_call(
                '\nFor this.json\nLoaded 0 lookup lists\n\n\nNew items report:\n\n\n0 new items 0 new synonyms'
            )


    def test_handle(self):
        c = loader.Command()
        with patch.object(c, 'stdout') as stdout:
            c.handle()
            stdout.write.assert_any_call(
                '\nFor SearchPlugin\nLoaded 0 lookup lists\n\n\nNew items report:\n\n\n0 new items 0 new synonyms'
            )

    def test_handle_with_filename(self):
        c = loader.Command()
        with patch.object(c, 'handle_explicit_filename') as handler:
            c.handle(filename="this.json")
            handler.assert_called_with(filename='this.json')
