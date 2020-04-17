from opal.management.commands import scaffold
from opal.core.test import OpalTestCase
from unittest.mock import patch, MagicMock


@patch("opal.management.commands.scaffold.core_scaffold")
class CommandTestCase(OpalTestCase):
    def setUp(self):
        self.c = scaffold.Command()

    def test_check_args(self, core_scaffold):
        self.c.handle(app="app", no_migrations=True, dry_run=False)
        core_scaffold.scaffold_subrecords.assert_called_once_with(
            "app", migrations=False, dry_run=False
        )

    def test_parser(self, core_scaffold):
        parser = MagicMock()
        self.c.add_arguments(parser)
        args_list = parser.add_argument.call_args_list
        self.assertEqual(
            args_list[0][0], ('app',),
        )
        self.assertEqual(
            args_list[0][1], dict(help="Specify an app")
        )
        self.assertEqual(
            args_list[1][0], ('--dry-run',),
        )
        self.assertEqual(
            args_list[1][1], dict(action='store_true')
        )
        self.assertEqual(
            args_list[2][0], ('--no-migrations',),
        )
        self.assertEqual(
            args_list[2][1], dict(action='store_true')
        )
