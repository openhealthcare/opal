"""
Unittests for opal.management.commands.dump_lookup_lists
"""
import os

from django.contrib.contenttypes.models import ContentType
from unittest.mock import patch, call, mock_open, MagicMock

from opal.core.test import OpalTestCase
from opal.models import Symptom, Synonym

from opal.management.commands import dump_lookup_lists as dll

class CreateSingletonsTestCase(OpalTestCase):

    def test_add_arguments(self):
        c = dll.Command()
        parser = MagicMock(name='Argument Parser')
        c.add_arguments(parser)
        parser.add_argument.assert_called_once_with(
            '--many-files',
            help="Write the lookuplists to many different files in ./data/lookuplists",
            action="store_true",
            dest="many_files"
        )

    def test_write_to_file(self):
        c = dll.Command()
        m = mock_open()
        with patch.object(c.stdout, 'write') as writer:
            with patch('opal.management.commands.dump_lookup_lists.open', m, create=True):
                c.write_to_file({}, '/tmp/no.json')
        m.assert_called_once_with('/tmp/no.json', 'w')
        handle = m()
        handle.write.assert_called_once_with('{}')

    def test_write_many_files(self):
        data = {
            'one': {},
            'two': {}
        }
        c = dll.Command()
        app_dir = dll.application.get_app().directory()
        dir_one = os.path.join(app_dir, 'data', 'lookuplists', 'one.json')
        dir_two = os.path.join(app_dir, 'data', 'lookuplists', 'two.json')
        with patch.object(c, 'write_to_file') as file_writer:
            c.write_to_many_files(data)
            calls = [
                call({'one': {}}, dir_one),
                call({'two': {}}, dir_two)
            ]
            file_writer.assert_has_calls(calls, any_order=True)

    def test_handle(self):
        sympt = Symptom.objects.create(
            name='Headache', code='HED', system='TLA'
        )
        Synonym.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(Symptom),
            object_id=sympt.id,
            name='Bad Head'
        )
        c = dll.Command()
        with patch.object(c.stdout, 'write') as writer:
            c.handle()
            self.assertEqual(1, writer.call_count)

    def test_handle_many_files(self):
        c = dll.Command()
        with patch.object(c, 'write_to_many_files') as writemany:
            c.handle(many_files=True)
            self.assertEqual(1, writemany.call_count)
