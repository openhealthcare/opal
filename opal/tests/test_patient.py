"""
Unittests for Patients
"""
import datetime

from unittest.mock import patch
from opal.core.test import OpalTestCase

from opal.models import Patient, Episode
from opal.tests.models import InvisibleDog


class PatientTest(OpalTestCase):

    def setUp(self):
        self.patient = Patient.objects.create()

    def test_singleton_subrecord_created(self):
        self.assertEqual(1, self.patient.famouslastwords_set.count())

    def test__str__(self):
        expected = 'Patient {}'.format(self.patient.pk)
        self.assertEqual(expected, self.patient.__str__())

    def test_can_create_episode(self):
        episode = self.patient.create_episode()
        self.assertEqual(Episode, type(episode))

    def test_get_active_episode(self):
        self.patient.create_episode()
        episode2 = self.patient.create_episode()
        episode2.active = True
        episode2.save()
        self.assertEqual(episode2.id, self.patient.get_active_episode().id)

    def test_get_active_episode_with_no_episodes(self):
        self.assertIsNone(self.patient.get_active_episode())

    def test_get_active_episode_with_no_active_episodes(self):
        self.patient.create_episode(end=datetime.date.today())
        self.patient.create_episode(end=datetime.date.today())
        self.assertIsNone(self.patient.get_active_episode())
