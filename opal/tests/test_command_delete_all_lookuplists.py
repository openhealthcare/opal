"""
Unittests for the delete all lookuplists command
"""
from django.contrib.contenttypes.models import ContentType

from opal.core.test import OpalTestCase
from opal.models import Symptom, Synonym

from opal.management.commands import delete_all_lookup_lists

class DeleteLookupListsTestCase(OpalTestCase):
    def test_deletes_lookuplist(self):
        self.assertEqual(0, Symptom.objects.count())
        sympt = Symptom.objects.create(name='Headache')
        Synonym.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(Symptom),
            object_id=sympt.id,
            name='Bad Head'
        )
        self.assertEqual(1, Symptom.objects.count())
        self.assertEqual(1, Synonym.objects.count())

        cmd = delete_all_lookup_lists.Command()
        cmd.handle()

        self.assertEqual(0, Symptom.objects.count())
        self.assertEqual(0, Synonym.objects.count())
