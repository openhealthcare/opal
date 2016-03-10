"""
This module defines the base PatientList classes.
"""
from opal.models import Episode, UserProfile
from opal.core import discoverable


class PatientList(discoverable.DiscoverableFeature):
    """
    A view of a list shown on the list page, complete with schema that
    define the columns shown and a queryset that defines the episodes shown
    """
    module_name = 'patient_lists'
    template_name = 'episode_list.html'
    order       = None

    @classmethod
    def list(klass):
        """
        Return an iterable of Patient Lists.
        """
        klasses = sorted(super(PatientList, klass).list(), key=lambda x: x.order)
        klasses.remove(TaggedPatientList)
        return klasses

    @classmethod
    def for_user(klass, user):
        """
        Return the set of instances that this USER can see.
        """
        for k in klass.list():
            if k.visible_to(user):
                yield k

    @classmethod
    def visible_to(klass, user):
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if profile.restricted_only:
            return False

        return True

    @property
    def schema(self):
        raise ValueError("this needs to be implemented")

    @property
    def queryset(self):
        raise ValueError("this needs to be implemented")

    def get_queryset(self):
        return self.queryset

    def get_template_names(self):
        return [self.template_name]

    def to_dict(self, user):
        # only bringing in active seems a sensible default at this time
        return self.get_queryset().serialised_active(user)


class TaggedPatientList(PatientList):
    """
    The most common list use case of a patient list, when we define a tag
    and a sub tag and look up the episodes on the basis of these. You still
    need to define schema
    """
    tag = "Implement me please"

    @classmethod
    def slug(klass):
        """
        For a tagged patient list, the slug is made up of the tags.
        """
        s = klass.tag
        if hasattr(klass, 'subtag'):
            s += '-' + klass.subtag
        return s

    def get_queryset(self):
        filter_kwargs = dict(tagging__archived=False)
        if getattr(self, "subtag", None):
            filter_kwargs["tagging__team__name"] = self.subtag
        else:
            filter_kwargs["tagging__team__name"] = self.tag
        return Episode.objects.filter(**filter_kwargs)
