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
from django.db import transaction
from django.utils import timezone
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

    @transaction.atomic
    def set_stage(self, stage_value, user, data):
        """
        Setter for Episode.stage

        Validates that the stage being set is appropriate for the category
        and raises ValueError if not.
        """
        if not self.has_stage(stage_value):
            if stage_value is not None:
                msg = "Can't set stage to {0} for {1} Episode".format(
                    stage_value, self.display_name
                )
                raise ValueError(msg)

        current_stage = self.episode.stage_set.filter(stopped=None).last()

        # if the stage hasn't changed, don't do anything
        if current_stage and current_stage.value == stage_value:
            return

        now = timezone.now()
        if current_stage:
            current_stage.stopped = now
            current_stage.updated = now
            current_stage.updated_by = user
            current_stage.save()

        if current_stage and not stage_value:
            raise ValueError(
                "A stage cannot be removed after one has been set")

        if stage_value:
            self.episode.stage_set.create(
                value=stage_value,
                started=now,
                created=now,
                created_by=user,
            )


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
