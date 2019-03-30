"""
Opal Episode categories

An episode of care in Opal can be one of many things:

An inpatient admission
A course of outpatient treatment
A visit to a drop in clinic
A liaison service performed for a patient (possibly across multiple episodes)
A research study enrollment

(Non exhaustive list)

An Episode category has various properties it can use to customise the way
episodes of it's category behave in Opal applications - for instance:

Display
Permissions

By registering episode category, plugins and applications can achieve a huge
degree of flexibility over the behaviour of their episodes.
"""
from opal.core.discoverable import DiscoverableFeature


class EpisodeCategory(DiscoverableFeature):
    module_name     = "episode_categories"
    display_name    = None
    detail_template = None
    stages          = []

    @classmethod
    def episode_visible_to(kls, episode, user):
        """
        Predicate function to determine whether an episode of this category
        is visible to a particular user.

        Defaults implementation checks for Profile.restricted_only and
        returns true if we have a regular user.
        """
        from opal.models import UserProfile  # Avoid circular import

        profile = UserProfile.objects.get(user=user)
        if profile.restricted_only:
            return False

        return True

    def __init__(self, episode):
        self.episode = episode

    def is_active(self):
        """
        Predicate function to determine whether this episode is active.

        The default implementation looks to see whether an end date has
        been set on the episode.
        """
        return bool(self.episode.end is None)

    def get_stages(self):
        """
        Return the list of string stages for this category
        """
        return [s for s in self.stages]

    def has_stage(self, stage):
        """
        Predicate function to determine whether STAGE is a valid stage
        for this category.
        """
        return stage in self.get_stages()

    def set_stage(self, stage, user, data):
        """
        Setter for Episode.stage

        Validates that the stage being set is appropriate for the category
        and raises ValueError if not.
        """
        if not self.has_stage(stage):
            if stage is not None:
                msg = "Can't set stage to {0} for {1} Episode".format(
                    stage, self.display_name
                )
                raise ValueError(msg)
        self.episode.stage = stage


class InpatientEpisode(EpisodeCategory):
    display_name    = 'Inpatient'
    detail_template = 'detail/inpatient.html'
    stages          = [
        'Inpatient',
        'Followup',
        'Discharged'
    ]
