"""
Unittests for opal.core.episodes
"""
from django.contrib.auth.models import User

from opal.core import test
from opal.models import UserProfile, Patient

from opal.core import episodes

class EpisodeCategoryTestCase(test.OpalTestCase):

    def setUp(self):
        self.restricted_user = User.objects.create(username='restrictedonly')
        self.profile, _ = UserProfile.objects.get_or_create(
            user=self.restricted_user, restricted_only=True
        )
        self.patient = Patient.objects.create()
        self.inpatient_episode = self.patient.create_episode(category=episodes.InpatientEpisode)

    def test_episode_categories(self):
        self.assertIn(episodes.InpatientEpisode, episodes.EpisodeCategory.list())

    def test_visible_to(self):
        self.assertTrue(
            episodes.InpatientEpisode.episode_visible_to(self.inpatient_episode, self.user))

    def test_visible_to_restricted_only(self):
        self.assertFalse(
            episodes.InpatientEpisode.episode_visible_to(self.inpatient_episode,
                                                         self.restricted_user)
        )

    def test_for_category(self):
        self.assertEqual(episodes.InpatientEpisode, episodes.EpisodeCategory.get('inpatient'))
