"""
Unittests for opal.core.episodes
"""
from opal.core import test

from opal.core import episodes

class EpisodeTypesTestCas(test.OpalTestCase):
    def test_episode_types(self):
        self.assertIn(episodes.InpatientEpisode, episodes.episode_types())
