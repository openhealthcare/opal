"""
Unittests for opal.management.commands.dump_lookup_lists
"""
from django.contrib.contenttypes.models import ContentType
from mock import patch

from opal.core.test import OpalTestCase
from opal.models import Symptom, Synonym

from opal.management.commands import dump_lookup_lists as dll

class CreateSingletonsTestCase(OpalTestCase):

    def test_handle(self):
        sympt = Symptom.objects.create(name='Headache')
        Synonym.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(Symptom),
            object_id=sympt.id,
            name='Bad Head'
        )
        c = dll.Command()
        with patch.object(c.stdout, 'write') as writer:
            c.handle()
            self.assertEqual(1, writer.call_count)
