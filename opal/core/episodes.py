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
Flow

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

        profile, _ = UserProfile.objects.get_or_create(user=user)
        if profile.restricted_only:
            return False

        return True

    def __init__(self, episode):
        self.episode = episode

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

    def next_stage(self):
        """
        Return the next stage for this episode or None if there is
        no future stage.
        """
        stages = self.get_stages()
        stage_index = stages.index(self.episode.stage)
        next_stage = stage_index + 1
        if next_stage + 1 == len(stages):
            return None
        return stages[next_stage]

    def advance_stage(self):
        """
        Update the episode to be at the next stage.
        """
        next_stage = self.next_stage()
        if next_stage:
            self.episode.stage = next_stage
            self.episode.save()



class InpatientEpisode(EpisodeCategory):
    display_name    = 'Inpatient'
    detail_template = 'detail/inpatient.html'
    stages          = [
        'Inpatient',
        'Followup',
        'Discharged'
    ]


class OutpatientEpisode(EpisodeCategory):
    display_name = 'Outpatient'
    stages       = [
        'Outpatient',
        'Discharged'
    ]


class LiaisonEpisode(EpisodeCategory):
    display_name = 'Liaison'
    stages       = [
        'Review',
        'Unfollow'
    ]
