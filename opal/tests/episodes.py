"""
Episode types to use when testing OPAL
"""
from opal.core import episodes

class RestrictedEpisodeType(episodes.EpisodeType):
    name = 'Restricted'

    @classmethod
    def episode_visible_to(kls, episode, user):
        return not bool(super(RestrictedEpisodeType, kls).episode_visible_to(episode, user))
