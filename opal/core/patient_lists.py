"""
This module defines the base PatientList classes.
"""
from opal import utils
from opal.core import discoverable, exceptions, menus, metadata


class Column(object):

    def __init__(self,
                 name=None, title=None, singleton=None, icon=None,
                 limit=None, template_path=None, detail_template_path=None):
        """
        Set up initial properties from either models or explicit arguments
        """

        self.name                 = name
        self.title                = title
        self.single               = singleton
        self.icon                 = icon
        self.list_limit           = limit
        self.template_path        = template_path
        self.detail_template_path = detail_template_path

        required = ['title', 'template_path']
        for attr in required:
            if getattr(self, attr) is None:
                raise ValueError(
                    'Column must have a {0}'.format(attr))

    def get_template_path(self, patient_list):
        """
        Getter method for the template path for this column
        """
        return self.template_path

    def get_detail_template_path(self, patient_list):
        """
        Getter method for the detail template path for this column
        """
        return self.detail_template_path

    def to_dict(self, patient_list=None, **kwargs):
        return dict(
            name=self.name,
            title=self.title,
            single=self.single,
            icon=self.icon,
            list_limit=self.list_limit,
            template_path=self.get_template_path(patient_list),
            detail_template_path=self.get_detail_template_path(patient_list)
        )


class ModelColumn(Column):

    def __init__(self, model):
        self.model = model

        from opal.models import Subrecord
        if not issubclass(model, Subrecord):
            raise ValueError('Model must be a opal.models.Subrecord subclass')

        self.name       = model.get_api_name()
        self.title      = model.get_display_name()
        self.single     = model._is_singleton
        self.icon       = getattr(model, '_icon', '')
        self.list_limit = getattr(model, '_list_limit', None)

    def get_template_path(self, patient_list):
        """
        Getter method for the template path for this column
        """
        return self.model.get_display_template(
            patient_list().get_template_prefixes()
        )

    def get_detail_template_path(self, patient_list):
        """
        Getter method for the detail template path for this column
        """
        return self.model.get_detail_template(
            prefixes=patient_list().get_template_prefixes()
        )

    def to_dict(self, patient_list=None, **kwargs):
        dicted = super(ModelColumn, self).to_dict(
            patient_list=patient_list, **kwargs
        )
        dicted['model_column'] = True
        return dicted


class PatientList(discoverable.DiscoverableFeature,
                  discoverable.RestrictableFeature):
    """
    A view of a list shown on the list page, complete with schema that
    define the columns shown and a queryset that defines the episodes shown
    """
    module_name        = 'patient_lists'
    template_name      = 'patient_lists/layouts/spreadsheet_list.html'
    order              = 0
    comparator_service = None
    icon               = None
    display_name       = None
    # whether we display the add patient button
    allow_add_patient  = True

    # whether we allow the user to edit the teams the patient is under
    allow_edit_teams = True

    @classmethod
    def get_absolute_url(klass, **kwargs):
        """
        Return the absolute URL for this list
        """
        return '/#/list/{0}'.format(klass.get_slug())

    @classmethod
    def get_icon(klass):
        """
        Default getter function - returns the `icon` proprety
        """
        return klass.icon

    @classmethod
    def get_display_name(klass):
        """
        Default getter function - returns the `display_name` property
        """
        return klass.display_name

    @classmethod
    def list(klass):
        """
        Return an iterable of Patient Lists.
        """
        return sorted(super(PatientList, klass).list(), key=lambda x: x.order)

    @classmethod
    def visible_to(klass, user):
        from opal.models import UserProfile  # Avoid circular import

        profile = UserProfile.objects.get(user=user)
        if profile.restricted_only:
            return False

        return True

    @classmethod
    def as_menuitem(kls, **kwargs):
        """
        Return an instance of `opal.core.menus.MenuItem` that will
        direct the user to this patient list.
        """
        return menus.MenuItem(
            href=kwargs.get('href', kls.get_absolute_url()),
            activepattern=kwargs.get('activepattern', kls.get_absolute_url()),
            icon=kwargs.get('icon', kls.get_icon()),
            display=kwargs.get('display', kls.get_display_name()),
            index=kwargs.get('index', '')
        )

    def get_template_prefixes(self):
        """
        A patient list can return templates particular to themselves
        or indeed used by other patient lists
        """
        return []

    @property
    def schema(self):
        raise ValueError("this needs to be implemented")

    @classmethod
    def schema_to_dicts(klass):
        columns = []

        for column in klass.schema:
            if isinstance(column, Column):
                columns.append(column.to_dict())
            else:
                columns.append(ModelColumn(column).to_dict(patient_list=klass))
        return columns

    @property
    def queryset(self):
        raise ValueError("this needs to be implemented")

    def get_queryset(self, user=None):
        return self.queryset

    def get_template_names(self):
        return [self.template_name]

    def to_dict(self, user):
        from opal.models import Episode
        return Episode.objects.serialised(user, self.get_queryset(user=user))


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

    def get_queryset(self, **kwargs):
        from opal.models import Episode  # Avoid circular import in opal.models

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
        if len(list(klass.get_member_lists_for_user(user))) > 1:
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
        except StopIteration:  # No lists for this user
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

        if user.is_authenticated:
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

        return data


class PatientListComparatorMetadata(metadata.Metadata):
    slug = 'patient_list_comparators'

    @classmethod
    def to_dict(klass, user=None, **kw):
        lists = [p for p in PatientList.for_user(user) if p.comparator_service]
        return {klass.slug: {
            plist.get_slug(): plist.comparator_service for plist in lists
        }}
