"""
Unit tests for OPAL.
"""
from django.contrib.auth.models import User
from django.test import TestCase

from opal.models import Patient, Episode

class PatientTest(TestCase):
    fixtures = ['patients_users', 'patients_records', 'patients_options']
    maxDiff = None

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.patient = Patient.objects.create()

    def test_demographics_subrecord_created(self):
        self.assertEqual(1, self.patient.demographics_set.count())

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

    def test_cannot_create_episode_if_has_active_episode(self):
        episode = self.patient.create_episode()
        episode.set_tag_names(['microbiology'], None)
        with self.assertRaises(Exception):
            self.patient.create_episode()


class EpisodeTest(TestCase):
    fixtures = ['patients_users', 'patients_records']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.patient = Patient.objects.create()
        self.episode = self.patient.create_episode()

    def test_location_subrecord_created(self):
        self.assertEqual(1, self.episode.location_set.count())

    def test_can_set_tag_names(self):
        for tag_names in [
            ['microbiology', 'mine'],
            ['microbiology', 'hiv'],
            ['hiv', 'mine'],
        ]:
            self.episode.set_tag_names(tag_names, self.user)
            self.assertEqual(set(tag_names),
                             set(self.episode.get_tag_names(self.user)))

    def test_user_cannot_see_other_users_mine_tag(self):
        other_user = User.objects.get(pk=2)

        self.episode.set_tag_names(['hiv', 'mine'], self.user)
        self.assertEqual(['hiv'], self.episode.get_tag_names(other_user))

    def test_active_if_tagged_by_non_mine_tag(self):
        self.episode.set_tag_names(['microbiology'], self.user)
        self.assertTrue(self.episode.is_active())

    def test_inactive_if_only_tagged_by_mine_tag(self):
        self.episode.set_tag_names(['mine'], self.user)
        self.assertFalse(self.episode.is_active())

    def test_to_dict(self):
        expected_data = {
            'id': self.episode.id,
            'demographics': [{
                'id': self.patient.demographics_set.get().id,
                'patient_id': self.patient.id,
                'consistency_token': '',
                'date_of_birth': None,
                'hospital_number': '',
                'name': '',
                }],
            'location': [{
                'id': self.episode.location_set.get().id,
                'episode_id': self.episode.id,
                'bed': '',
                'category': '',
                'consistency_token': '',
                'date_of_admission': None,
                'discharge_date': None,
                'hospital': '',
                'tags': {},
                'ward': '',
                }],
            'diagnosis': [],
            'past_medical_history': [],
            'general_note': [],
            'travel': [],
            'antimicrobial': [],
            'microbiology_input': [],
            'todo': [],
            'microbiology_test': [],
        }
        self.assertEqual(expected_data, self.episode.to_dict(self.user))
