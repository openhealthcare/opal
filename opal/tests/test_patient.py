"""
Unittests for Patients
"""
from django.contrib.auth.models import User
from django.test import TestCase

from opal.models import Patient, Team, Episode

class PatientTest(TestCase):

    def setUp(self):
        self.patient = Patient.objects.create()
        self.micro   = Team.objects.create(name='microbiology', title='microbiology')

    def test_singleton_subrecord_created(self):
        self.assertEqual(1, self.patient.famouslastwords_set.count())

    def test_can_create_episode(self):
        episode = self.patient.create_episode()
        self.assertEqual(Episode, type(episode))

    def test_get_active_episode(self):
        episode1 = self.patient.create_episode()
        episode2 = self.patient.create_episode()
        episode2.set_tag_names(['microbiology'], None)
        self.assertEqual(episode2.id, self.patient.get_active_episode().id)

    def test_get_active_episode_with_no_episodes(self):
        self.assertIsNone(self.patient.get_active_episode())

    def test_get_active_episode_with_no_active_episodes(self):
        self.patient.create_episode()
        self.patient.create_episode()
        self.assertIsNone(self.patient.get_active_episode())

