from opal.models import Episode, Team
from django.utils.functional import cached_property
from django.utils.text import slugify

"""
This module defines the base PatientList classes.
"""
from opal.models import Episode
from opal.core import discoverable


class PatientList(discoverable.DiscoverableFeature):
    """
    A view of a list shown on the list page, complete with schema that
    define the columns shown and a queryset that defines the episodes shown
    """
    module_name = 'patient_lists'

    def __init__(self, request, *args, **kwargs):
        self.request = request

    @property
    def order(self):
        raise ValueError("this needs to be implemented")

    @property
    def schema(self):
        raise ValueError("this needs to be implemented")

    @property
    def queryset(self):
        raise ValueError("this needs to be implemented")

    @property
    def title(self):
        return self.name.title()

    def visibile_to_user(self):
        return True

    def get_queryset(self):
        return self.queryset

    # def to_dict(self, user):
    #     # only bringing in active seems a sensible default at this time
    #     return self.get_queryset().serialised_active(self.request.user)

    def to_dict(self):
        return dict(
            title=self.title,
            slug=self.__class__.slug()
        )

    @classmethod
    def get_menu_items(klass, request):
        list_classes = klass.list()
        objects = [patient_list(request) for patient_list in list_classes]
        return [o for o in objects if o.visibile_to_user()]


class TaggedPatientList(PatientList):
    """
    The most common list use case of a patient list, when we define a tag
    and a sub tag and look up the episodes on the basis of these. You still
    need to define schema
    """
    tag = "Implement me please"
    order = 3

    @cached_property
    def title(self):
        tag_obj = Team.objects.get(name=self.tag)

        if self.name != self.tag:
            subtag_obj = Team.objects.get(name=self.name)
            return "{0} / {1}".format(tag_obj.title, subtag_obj.title)
        else:
            return tag_obj.title

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
        filter_kwargs["tagging__team__name"] = self.name
        return Episode.objects.filter(**filter_kwargs)

    def visibile_to_user(self):
        return not self.__class__.__name__ == "TaggedPatientList"
