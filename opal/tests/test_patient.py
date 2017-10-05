"""
Unittests for Patients
"""
from __future__ import unicode_literals

from opal.core.test import OpalTestCase
from opal.models import Patient, Episode


class PatientTest(OpalTestCase):

    def setUp(self):
        self.patient = Patient.objects.create()

    def test_to_string_with_demographics(self):
        self.patient.demographics_set.update(
            hospital_number="123",
            first_name="Wilma",
            surname="Flintstone"
        )
        self.assertEqual(
            str(self.patient),
            "Patient: 123 - Wilma Flintstone"
        )

    def test_to_string_without_demographics(self):
        self.patient.demographics_set.all().delete()
        self.assertEqual(
            str(self.patient),
            "Patient: 1"
        )

    def test_singleton_subrecord_created(self):
        self.assertEqual(1, self.patient.famouslastwords_set.count())

    def test_can_create_episode(self):
        episode = self.patient.create_episode()
        self.assertEqual(Episode, type(episode))

    def test_get_active_episode(self):
        self.patient.create_episode()
        episode2 = self.patient.create_episode()
        episode2.set_tag_names(['microbiology'], None)
        self.assertEqual(episode2.id, self.patient.get_active_episode().id)

    def test_get_active_episode_with_no_episodes(self):
        self.assertIsNone(self.patient.get_active_episode())

    def test_get_active_episode_with_no_active_episodes(self):
        self.patient.create_episode()
        self.patient.create_episode()
        self.assertIsNone(self.patient.get_active_episode())
