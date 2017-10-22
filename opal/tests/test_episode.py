"""
Unittests for opal.models.Episode
"""
from __future__ import unicode_literals

import datetime
from mock import patch, MagicMock

from django.contrib.auth.models import User

from six import text_type
from opal.core.episodes import InpatientEpisode
from opal.core.test import OpalTestCase
from opal.models import Patient, Episode, Tagging, UserProfile
from opal.tests import test_patient_lists  # NOQA ensure the lists are loaded

from opal.tests.models import (
    Hat, HatWearer, InvisibleHatWearer
)


class EpisodeTest(OpalTestCase):

    def setUp(self):
        self.patient, self.episode = self.new_patient_and_episode_please()
        self.episode.stage = "Active TB"
        self.episode.save()

    def test_unicode(self):
        self.episode.start = datetime.date(2017, 1, 1)
        self.episode.save()
        self.patient.demographics_set.update(
            first_name="Wilma", surname="Flintstone", hospital_number="123"
        )
        self.assertEqual(
            text_type(self.episode),
            "Episode: 1 - 123 - Wilma Flintstone - 2017-01-01"
        )

    def test_unicode_without_start(self):
        self.patient.demographics_set.update(
            first_name="Wilma", surname="Flintstone", hospital_number="123"
        )
        self.assertEqual(
            text_type(self.episode),
            "Episode: 1 - 123 - Wilma Flintstone - None"
        )

    def test_unicode_without_demographics(self):
        self.patient.demographics_set.all().delete()
        self.episode.start = datetime.date(2017, 1, 1)
        self.episode.save()
        self.assertEqual(
            text_type(self.episode),
            "Episode: 1 - 2017-01-01"
        )

    def test_unicode_without_demographics_without_start(self):
        self.patient.demographics_set.all().delete()
        self.assertEqual(
            text_type(self.episode),
            "Episode: 1 - None"
        )

    def test_singleton_subrecord_created(self):
        self.assertEqual(1, self.episode.episodename_set.count())

    def test_category(self):
        self.episode.category_name = 'Inpatient'
        self.assertEqual(self.episode.category.__class__, InpatientEpisode)
        self.assertEqual(self.episode.category.episode, self.episode)

    def test_visible_to(self):
        self.assertTrue(self.episode.visible_to(self.user))

    def test_can_set_tag_names(self):
        test_cases = [
            ['microbiology', 'mine'],
            ['microbiology', 'hiv'],
            ['hiv', 'mine'],
        ]

        for tag_names in test_cases:
            self.episode.set_tag_names(tag_names, self.user)
            self.assertEqual(set(tag_names),
                             set(self.episode.get_tag_names(self.user)))

    def test_set_tagging_parent(self):
        self.episode.set_tag_names(["mine", "herbivore"], self.user)

        self.assertTrue(Tagging.objects.filter(
            value='eater', archived=False).exists()
        )
        self.assertTrue(Tagging.objects.filter(
            value='herbivore', archived=False).exists()
        )
        self.assertTrue(Tagging.objects.filter(
            value='mine', user=self.user, archived=False).exists()
        )

    def test_user_cannot_see_other_users_mine_tag(self):
        other_user = User.objects.create(username='seconduser')
        self.episode.set_tag_names(['carnivore', 'mine'], self.user)
        self.assertEqual(['carnivore'], list(self.episode.get_tag_names(other_user)))

    def test_active_if_tagged_by_non_mine_tag(self):
        self.episode.set_tag_names(['carnivore'], self.user)
        self.assertTrue(self.episode.active)

    def test_active_if_only_tagged_by_mine_tag(self):
        self.episode.set_tag_names(['mine'], self.user)
        self.assertTrue(self.episode.active)

    def test_to_dict_fields(self):
        as_dict = self.episode.to_dict(self.user)
        expected = [
            'id', 'category_name', 'active',
            'consistency_token', 'start', 'end', 'stage'
        ]
        for field in expected:
            self.assertIn(field, as_dict)

        self.assertEqual(as_dict["stage"], "Active TB")

    def test_get_field_names_to_extract(self):
        # field names to extract should be the same
        # as the field names to serialise
        self.assertEqual(
            Episode._get_fieldnames_to_serialize(),
            Episode._get_fieldnames_to_extract()
        )

    @patch('opal.models.episode_subrecords')
    def test_not_bulk_serialisable_episode_subrecords(self, episode_subrecords):
        episode_subrecords.return_value = [InvisibleHatWearer]
        _, episode = self.new_patient_and_episode_please()
        to_dict = episode.to_dict(self.user)
        self.assertNotIn(InvisibleHatWearer.get_api_name(), to_dict)


    def test_to_dict_with_multiple_episodes(self):
        self.episode.start = datetime.date(2015, 7, 25)
        self.episode.save()
        prev = self.patient.create_episode()
        prev.start = datetime.date(2012, 7, 25)
        prev.end = datetime.date(2012, 8, 12)
        prev.active=False
        prev.save()

        serialised = self.episode.to_dict(self.user)
        self.assertEqual(2, len(serialised['episode_history']))
        self.assertEqual(datetime.date(2012, 7, 25),
                         serialised['episode_history'][0]['start'])

    def test_to_dict_episode_ordering(self):
        patient = Patient.objects.create()
        prev = patient.create_episode()
        prev.start = datetime.date(2012, 7, 25)
        prev.end = datetime.date(2012, 8, 12)
        prev.active = False
        prev.save()

        previouser = patient.create_episode()
        previouser.start = datetime.date(2011, 7, 25)
        previouser.active = False
        previouser.save()

        episode = patient.create_episode()
        episode.start = datetime.date(2014, 6, 23)
        episode.save()

        serialised = episode.to_dict(self.user)
        self.assertEqual(3, len(serialised['episode_history']))
        self.assertEqual(datetime.date(2011, 7, 25),
                         serialised['episode_history'][0]['start'])
        self.assertEqual(datetime.date(2012, 7, 25),
                         serialised['episode_history'][1]['start'])

    def test_to_dict_episode_history_includes_no_dates(self):
        prev = self.patient.create_episode()
        serialised = self.episode.to_dict(self.user)
        self.assertEqual(2, len(serialised['episode_history']))

    @patch('opal.models.episode_subrecords')
    def test_to_dict_episode_with_many_to_many(self, episode_subrecords):
        episode_subrecords.return_value = [HatWearer]
        prev = self.patient.create_episode()
        bowler = Hat.objects.create(name="bowler")
        top = Hat.objects.create(name="top")
        hw = HatWearer.objects.create(episode=prev)
        hw.hats.add(bowler, top)
        serialised = prev.to_dict(self.user)
        self.assertEqual(serialised["hat_wearer"][0]["hats"], [u'bowler', u'top'])


class EpisodeCategoryTestCase(OpalTestCase):
    def setUp(self):
        _, self.episode = self.new_patient_and_episode_please()
        self.today = datetime.date.today()
        self.yesterday = self.today - datetime.timedelta(1)

    def test_episode_visible_false(self):
        user = User.objects.create()
        UserProfile.objects.create(user=user, restricted_only=True)
        self.assertFalse(
            self.episode.category.episode_visible_to(self.episode, user)
        )

    def test_episode_visible_true(self):
        user = User.objects.create()
        UserProfile.objects.create(user=user, restricted_only=False)
        self.assertTrue(
            self.episode.category.episode_visible_to(self.episode, user)
        )
