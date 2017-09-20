"""
Episode types to use when testing OPAL
"""
from __future__ import unicode_literals

from opal.core import episodes

class RestrictedEpisodeCategory(episodes.EpisodeCategory):
    display_name = 'Restricted'

    @classmethod
    def episode_visible_to(kls, episode, user):
        return not bool(super(RestrictedEpisodeCategory, kls).episode_visible_to(episode, user))
