"""
This module defines the base PatientList classes.
"""
from opal import utils
from opal.models import Episode, UserProfile
from opal.core import discoverable, exceptions


class PatientList(discoverable.DiscoverableFeature,
                  discoverable.RestrictableFeature):
    """
    A view of a list shown on the list page, complete with schema that
    define the columns shown and a queryset that defines the episodes shown
    """
    module_name = 'patient_lists'
    template_name = 'patient_lists/spreadsheet_list.html'
    order       = None

    @classmethod
    def list(klass):
        """
        Return an iterable of Patient Lists.
        """
        return sorted(super(PatientList, klass).list(), key=lambda x: x.order)

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


class TaggedPatientList(PatientList, utils.AbstractBase):
    """
    The most common list use case of a patient list, when we define a tag
    and a sub tag and look up the episodes on the basis of these. You still
    need to define schema
    """
    direct_add = True
    tag = "Implement me please"
    display_name = "Implement me please"

    @classmethod
    def is_valid(klass):
        if '-' in klass.tag:
            msg = 'Invalid tag {0}'.format(klass.tag)
            raise exceptions.InvalidDiscoverableFeatureError(msg)
        if hasattr(klass, 'subtag'):
            if '-' in klass.subtag:
                msg = 'Invalid subtag {0}'.format(klass.subtag)
                raise exceptions.InvalidDiscoverableFeatureError(msg)
        return True

    @classmethod
    def get_slug(klass):
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
