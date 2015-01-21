"""
Unittests for Episodes
"""
import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from opal.models import Patient, Episode

class EpisodeTest(TestCase):
    fixtures = ['patients_users', 'patients_records', 'patients_options']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.patient = Patient.objects.create()
        self.episode = self.patient.create_episode()

    def test_unicode(self):
        self.assertEqual(' |  | None', self.episode.__unicode__())

    def test_location_subrecord_created(self):
        self.assertEqual(1, self.episode.location_set.count())

    def test_is_discharged_starts_false(self):
        self.assertEqual(False, self.episode.is_discharged)

    def test_is_discharged_inactive(self):
        self.episode.active = False
        self.assertEqual(True, self.episode.is_discharged)

    def test_is_discharged_from_date(self):
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        self.episode.discharge_date = yesterday
        self.assertEqual(True, self.episode.is_discharged)
        
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
        self.assertTrue(self.episode.active)

    def test_active_if_only_tagged_by_mine_tag(self):
        self.episode.set_tag_names(['mine'], self.user)
        self.assertTrue(self.episode.active)

    def test_to_dict_with_multiple_episodes(self):
        episode = Episode.objects.get(pk=1)
        serialised = episode.to_dict(self.user)
        self.assertEqual(1, len(serialised['prev_episodes']))
        self.assertEqual(datetime.date(2012, 7, 25),
                         serialised['prev_episodes'][0]['date_of_admission'])

    def test_to_dict_episode_ordering(self):
        episode = Episode.objects.get(pk=1)
        patient = episode.patient
        admitted = datetime.date(2011, 7, 25)
        new_episode = Episode(patient=patient, date_of_admission=admitted)
        new_episode.save()

        serialised = episode.to_dict(self.user)
        self.assertEqual(2, len(serialised['prev_episodes']))
        self.assertEqual(datetime.date(2011, 7, 25),
                         serialised['prev_episodes'][0]['date_of_admission'])
        self.assertEqual(datetime.date(2012, 7, 25),
                         serialised['prev_episodes'][1]['date_of_admission'])

