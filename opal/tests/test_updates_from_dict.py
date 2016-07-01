from django.test import TestCase
from django.db import models as djangomodels

from opal.models import UpdatesFromDictMixin

class UpdatesFromDictMixinTest(TestCase):
    class TestDiagnosis(UpdatesFromDictMixin, djangomodels.Model):
        condition = djangomodels.CharField(max_length=255, blank=True, null=True)
        provisional = djangomodels.BooleanField()
        details = djangomodels.CharField(max_length=255, blank=True)
        date_of_diagnosis = djangomodels.DateField(blank=True, null=True)

    def test_get_fieldnames_to_serialise(self):
        names = self.TestDiagnosis._get_fieldnames_to_serialize()
        expected = ['id', 'condition', 'provisional', 'details', 'date_of_diagnosis']
        self.assertEqual(expected, names)

    def test_get_named_foreign_key_fields(self):
        for name in ['patient_id', 'episode_id', 'gp_id', 'nurse_id']:
            self.assertEqual(djangomodels.ForeignKey,
                             self.TestDiagnosis._get_field_type(name))
