"""
Unittests for export command
"""
import json
from mock import MagicMock, patch
from opal.core.test import OpalTestCase

from opal.management.commands import export

class ExportTestCase(OpalTestCase):

    def test_add_arguments(self):
        c = export.Command()
        parser = MagicMock()
        c.add_arguments(parser)
        parser.add_argument.assert_any_call(
            '--patient',
            dest='patient',
            help='ID of the patient you would like to export',
            default=None
        )
        parser.add_argument.assert_any_call(
            '--exclude',
            dest='exclude',
            help='Comma separated list of subrecord api_names to exclude',
            default=""
        )

    def test_handle_patient_does_not_exist(self):
        c = export.Command()
        with self.assertRaises(LookupError):
            c.handle(patient='123')

    def test_handle_no_patient_argument(self):
        c = export.Command()
        with self.assertRaises(ValueError):
            c.handle()

    def test_handle_writes_json_output(self):
        p, e = self.new_patient_and_episode_please()
        c = export.Command()
        with patch.object(c.stdout, 'write') as writer:
            with patch.object(export.trade, 'patient_id_to_json') as serializer:
                serializer.return_value = dict(hello='world'), None

                c.handle(patient=str(p.id))
                self.assertEqual(1, writer.call_count)
                self.assertEqual(
                    dict(hello='world'),
                    json.loads((writer.call_args[0][0]))
                )

    def test_handle_passes_through_excludes(self):
        p, e = self.new_patient_and_episode_please()
        c = export.Command()
        with patch.object(c.stdout, 'write') as writer:
            with patch.object(export.trade, 'patient_id_to_json') as serializer:
                serializer.return_value = dict(hello='world'), None
                c.handle(patient=str(p.id), exclude='allergies')
                self.assertEqual(
                    ['allergies'],
                    serializer.call_args[1]['excludes']
                )
