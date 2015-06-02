"""
Unittests for the delete all lookuplists command
"""
from opal.core.test import OpalTestCase
from opal.models import Symptom

from opal.management.commands import delete_all_lookup_lists

class DeleteLookupListsTestCase(OpalTestCase):
    def test_deletes_lookuplist(self):
        self.assertEqual(0, Symptom.objects.count())
        Symptom.objects.create(name='Headache')
        self.assertEqual(1, Symptom.objects.count())
        
        cmd = delete_all_lookup_lists.Command()
        cmd.delete()

        self.assertEqual(0, Symptom.objects.count())
                                                    
