"""
Opal Episode categories

An episode of care in OPAL can be one of many things:

An inpatient admission
A course of outpatient treatment
A visit to a drop in clinic
A liaison service performed for a patient (possibly across multiple episodes)
A research study enrollment

(Non exhaustive list)

An Episode category has various properties it can use to customise the way
episodes of it's category behave in OPAL applications - for instance:

Display
Permissions
Flow

By registering episode category, plugins and applications can achieve a huge
degree of flexibility over the behaviour of their episodes.
"""
from opal.core.discoverable import DiscoverableFeature


class EpisodeCategory(DiscoverableFeature):
    module_name     = "episode_categories"
    display_name    = None
    detail_template = None

    @classmethod
    def episode_visible_to(kls, episode, user):
        """
        Predicate function to determine whether an episode of this category
        is visible to a particular user.

        Defaults implementation checks for Profile.restricted_only and
        returns true if we have a regular user.
        """
        from opal.models import UserProfile  # Avoid circular import

        profile, _ = UserProfile.objects.get_or_create(user=user)
        if profile.restricted_only:
            return False

        return True

    def __init__(self, episode):
        self.episode = episode


class InpatientEpisode(EpisodeCategory):
    display_name    = 'Inpatient'
    detail_template = 'detail/inpatient.html'


class OutpatientEpisode(EpisodeCategory):
    display_name = 'Outpatient'


class LiaisonEpisode(EpisodeCategory):
    display_name = 'Liaison'
