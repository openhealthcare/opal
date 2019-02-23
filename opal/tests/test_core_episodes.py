"""
Unittests for opal.core.episodes
"""
import datetime

from django.contrib.auth.models import User

from opal.core import test
from opal.models import UserProfile, Patient

from opal.core import episodes

class EpisodeCategoryTestCase(test.OpalTestCase):

    def setUp(self):
        self.restricted_user = User.objects.create(username='restrictedonly')
        UserProfile.objects.filter(
            user=self.restricted_user
        ).update(
            restricted_only=True
        )
        self.patient = Patient.objects.create()
        self.inpatient_episode = self.patient.create_episode(
            category_name=episodes.InpatientEpisode.display_name
        )

    def test_episode_categories(self):
        self.assertIn(
            episodes.InpatientEpisode, episodes.EpisodeCategory.list()
        )

    def test_visible_to(self):
        self.assertTrue(
            episodes.InpatientEpisode.episode_visible_to(
                self.inpatient_episode, self.user)
        )

    def test_visible_to_restricted_only(self):
        self.assertFalse(
            episodes.InpatientEpisode.episode_visible_to(
                self.inpatient_episode,
                self.restricted_user)
        )

    def test_for_category(self):
        self.assertEqual(episodes.InpatientEpisode,
                         episodes.EpisodeCategory.get('inpatient'))

    def test_is_active(self):
        category = episodes.InpatientEpisode(self.inpatient_episode)
        self.assertTrue(category.is_active())

    def test_is_active_end_date_set(self):
        self.inpatient_episode.end = datetime.date.today()
        category = episodes.InpatientEpisode(self.inpatient_episode)
        self.assertFalse(category.is_active())

    def test_get_stages(self):
        stages = [
            'Inpatient',
            'Followup',
            'Discharged'
        ]
        category = episodes.InpatientEpisode(self.inpatient_episode)
        self.assertEqual(stages, category.get_stages())

    def test_get_stages_unchanged(self):
        stages = [
            'Inpatient',
            'Followup',
            'Discharged'
        ]
        category = episodes.InpatientEpisode(self.inpatient_episode)
        stages1 = category.get_stages()
        stages1.append('hahhahahaha')
        self.assertEqual(stages, category.get_stages())

    def test_has_stage_true(self):
        category = episodes.InpatientEpisode(self.inpatient_episode)
        self.assertTrue(category.has_stage('Inpatient'))

    def test_has_stage_case_sensitive(self):
        category = episodes.InpatientEpisode(self.inpatient_episode)
        self.assertFalse(category.has_stage('inpatient'))

    def test_has_stage_false(self):
        category = episodes.InpatientEpisode(self.inpatient_episode)
        self.assertFalse(category.has_stage('Airegin'))

    def test_can_monkeypatch_stages(self):

        class ButterflyEpisode(episodes.EpisodeCategory):
            display_name = 'Butterfly'
            stages       = [
                'Caterpillar',
                'Cocoon',
            ]

        ButterflyEpisode.stages.append('Butterfly')

        self.assertTrue(ButterflyEpisode(None).has_stage('Butterfly'))
