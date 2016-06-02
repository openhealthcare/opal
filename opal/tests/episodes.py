"""
Episode types to use when testing OPAL
"""
from opal.core import episodes

class RestrictedEpisodePattern(episodes.EpisodePattern):
    display_name = 'Restricted'

    @classmethod
    def episode_visible_to(kls, episode, user):
        return not bool(super(RestrictedEpisodePattern, kls).episode_visible_to(episode, user))
