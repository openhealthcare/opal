"""
Unittests for import command
"""
from mock import MagicMock, mock_open, patch

from opal.core.test import OpalTestCase

from opal.management.commands import load

class LoadTestCase(OpalTestCase):

    def test_add_arguments(self):
        c = load.Command()
        parser = MagicMock()
        c.add_arguments(parser)
        parser.add_argument.assert_any_call(
            '--patient', '-p',
            dest='patient_file',
            help='Path to file containing a patient',
            default=None
        )

    def test_handle_no_patient_file(self):
        with self.assertRaises(ValueError):
            c = load.Command()
            c.handle()

    def test_handle_reads_file(self):
        c = load.Command()
        m = mock_open(read_data='{"when": "Night and day"}')
        with patch("__builtin__.open", m):
            with patch.object(load.trade, 'import_patient') as importer:
                c.handle(patient_file='data.json')
                importer.assert_called_with({"when": "Night and day"})
