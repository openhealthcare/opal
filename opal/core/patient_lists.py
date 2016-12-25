"""
This module defines the base PatientList classes.
"""
from opal import utils
from opal.core import discoverable, exceptions, metadata


class PatientList(discoverable.DiscoverableFeature,
                  discoverable.RestrictableFeature):
    """
    A view of a list shown on the list page, complete with schema that
    define the columns shown and a queryset that defines the episodes shown
    """
    module_name   = 'patient_lists'
    template_name = 'patient_lists/spreadsheet_list.html'
    order         = 0

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


"""
Sometimes we group lists for display purposes.
"""
class TabbedPatientListGroup(discoverable.DiscoverableFeature):
    """
    Groups of Patient Lists to display as tabs at the top of
    any list in the group
    """
    module_name   = 'patient_lists'
    member_lists  = []
    template_name = 'patient_lists/tabbed_list_group.html'

    @classmethod
    def get_template_names(klass):
        """
        A hook for dynamically customising the template_name(s) to be used
        for displaying the list group at the head of the list.

        Returns an iterable of template names.
        Defaults to the `.template_name` property
        """
        return [klass.template_name]

    @classmethod
    def get_template(klass):
        """
        Return the first existing template from .get_template_names() or None
        """
        return utils.find_template(klass.get_template_names())

    @classmethod
    def for_list(klass, patient_list):
        """
        Returns the group for a given PatientList.
        Raises ValueError if not passed a PatientList
        """
        msg = 'TabbedPatientListGroup.for_list must be passed a PatientList'
        try:
            if not issubclass(patient_list, PatientList):
                raise ValueError(msg)
        except TypeError:
                raise ValueError(msg)

        for group in klass.list():
            if patient_list in group.get_member_lists():
                return group

    @classmethod
    def get_member_lists(klass):
        """
        A hook for dynamically customising the members of this list group.

        Returns an iterable of PatientLists
        Defaults to the `.member_lists` property
        """
        for l in klass.member_lists:
            yield l

    @classmethod
    def get_member_lists_for_user(klass, user):
        """
        Returns an iterable of the visible member lists for a given USER
        """
        for l in klass.get_member_lists():
            if l.visible_to(user):
                yield l

    @classmethod
    def visible_to(klass, user):
        """
        Predicate function to determine whether this list is meaningfully
        visible to this USER
        """
        if len(list(klass.get_member_lists_for_user(user))) > 0:
            return True
        return False


"""
Begin Definitions of Patient List App Metadata entries
"""

class FirstListMetadata(metadata.Metadata):
    slug = 'first_list_slug'

    @classmethod
    def to_dict(klass, user=None, **kw):
        try:
            slug = next(PatientList.for_user(user)).get_slug()
        except StopIteration: # No lists for this user
            slug = ''
        return {
            klass.slug: slug
        }


class TaggedPatientListMetadata(metadata.Metadata):
    slug = 'tagging'

    @classmethod
    def to_dict(klass, user=None, **kw):
        data = {}
        tag_visible_in_list = []
        tag_direct_add = []
        tag_display = {}
        tag_slugs = {}
        tag_list = [i for i in TaggedPatientList.for_user(user)]

        if user.is_authenticated():
            for taglist in tag_list:
                slug = taglist().get_slug()
                tag = taglist.tag
                if hasattr(taglist, 'subtag'):
                    tag = taglist.subtag
                tag_display[tag] = taglist.display_name
                tag_slugs[tag] = slug
                tag_visible_in_list.append(tag)
                if taglist.direct_add:
                    tag_direct_add.append(tag)

        data['tag_display'] = tag_display
        data['tag_visible_in_list'] = tag_visible_in_list
        data['tag_direct_add'] = tag_direct_add
        data['tag_slugs'] = tag_slugs
        data["tags"] = {}

        for tagging in tag_list:
            tag = tagging.tag
            if hasattr(tagging, 'subtag'):
                tag = tagging.subtag

            direct_add = tagging.direct_add
            slug = tagging().get_slug()
            data["tags"][tag] = dict(
                name=tag,
                display_name=tagging.display_name,
                slug=slug,
                direct_add=direct_add
            )

            if tag and hasattr(tagging, 'subtag'):
                data["tags"][tag]["parent_tag"] = tagging.tag

        data["tags"]["mine"] = dict(
            name="mine",
            display_name="Mine",
            slug="mine",
            direct_add=True,
        )
        return data
