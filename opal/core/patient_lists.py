"""
This module defines the base PatientList classes.
"""
from opal import utils
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
        from opal.models import UserProfile # Avoid circular import from opal.models

        profile, _ = UserProfile.objects.get_or_create(user=user)
        if profile.restricted_only:
            return False

        return True

    def get_template_prefixes(self):
        """ a patient list can return templates particular to themselves
            or indeed used by other patient lists
        """
        return []

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

    @classmethod
    def get_tag_names(kls):
        tags = []
        for patientlist in kls.list():
            if patientlist.tag not in tags:
                tags.append(patientlist.tag)
            if hasattr(patientlist, 'subtag'):
                tags.append(patientlist.subtag)
        return tags

    def get_queryset(self):
        from opal.models import Episode # Avoid circular import from opal.models

        filter_kwargs = dict(tagging__archived=False)
        if getattr(self, "subtag", None):
            filter_kwargs["tagging__value"] = self.subtag
        else:
            filter_kwargs["tagging__value"] = self.tag
        return Episode.objects.filter(**filter_kwargs)

    def get_template_prefixes(self):
        """ a patient list can return templates particular to themselves
            or indeed used by other patient lists
        """
        possible = [self.tag]

        if hasattr(self, 'subtag'):
            possible.append("{0}.{1}".format(self.tag, self.subtag))
        return possible
