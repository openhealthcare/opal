"""
OPAL Episode types

An episode of care in OPAL can be one of many things:

An inpatient admission
A course of outpatient treatment
A visit to a drop in clinic
A liaison service performed on a patient (possibly across multiple other episodes)
A research study enrollment

(Non exhaustive list)

An Episode type has various properties it can use to customise the way episodes
of it's type behave in OPAL applications - for instance:

Display
Permissions
Flow

By registering episode types, plugins and applications can achieve a huge degree of
flexibility over the behaviour of their episodes.
"""
from opal.utils import _itersubclasses

class EpisodeType(object):
    name            = None
    detail_template = None

    @classmethod
    def episode_visible_to(kls, episode, user):
        """
        Predicate function to determine whether an episode of this type
        is visible to a particular user.

        Defaults implementation checks for Profile.restricted_only and
        returns true if we have a regular user.
        """
        from opal.models import UserProfile # Avoid circular import from opal.models

        profile, _ = UserProfile.objects.get_or_create(user=user)
        if profile.restricted_only:
            return False

        return True

    def __init__(self, episode):
        self.episode = episode

    @classmethod
    def for_category(kls, category):
        for et in episode_types():
            if et.name == category:
                return et

    @property
    def start(self):
        if self.episode.date_of_episode:
            return self.episode.date_of_episode
        else:
            return self.episode.date_of_admission

    @property
    def end(self):
        if self.episode.date_of_episode:
            return self.episode.date_of_episode
        else:
            return self.episode.discharge_date


class InpatientEpisode(EpisodeType):
    name            = 'Inpatient'
    detail_template = 'detail/inpatient.html'


class OutpatientEpisode(EpisodeType):
    name = 'Outpatient'


class LiaisonEpisode(EpisodeType):
    name = 'Liaison'


def episode_types():
    """
    Generator function for episode types
    """
    for et in _itersubclasses(EpisodeType):
        yield et
