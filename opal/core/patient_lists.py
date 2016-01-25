from opal.models import Episode, Team
from opal.core import app_importer
from django.utils.functional import cached_property


class PatientList(object):
    """
    A view of a list shown on the list page, complete with schema that
    define the columns shown and a queryset that defines the episodes shown
    """
    def __init__(self, request, *args, **kwargs):
        self.request = request

    @property
    def order(self):
        raise "this needs to be implemented"

    @property
    def schema(self):
        raise "this needs to be implemented"

    @property
    def queryset(self):
        raise "this needs to be implemented"

    @property
    def url(self):
        raise "this needs to be implemented"

    def visibile_to_user(self):
        return True

    def get_queryset(self):
        return self.queryset

    def get_serialised(self):
        # only bringing in active seems a sensible default at this time
        return self.get_queryset().serialised_active(self.request.user)

    def to_dict(self):
        return dict(
            title=self.title,
            url=self.url
        )

    @classmethod
    def list_classes(klass):
        return app_importer.get_subclass("patient_lists", klass)

    @classmethod
    def get_class(klass, request, **kwargs):
        list_classes = klass.list_classes()
        for list_class in list_classes:
            lc = list_class.get(request.user, **kwargs)
            if lc:
                patient_list = lc(request)
                if patient_list.visibile_to_user():
                    return patient_list

    @classmethod
    def get_menu_items(klass, request):
        list_classes = klass.list_classes()
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

    @property
    def url(self):
        if hasattr(self, "subtag"):
            return "#/list/{0}/{1}".format(self.tag, self.subtag)
        else:
            return "#/list/{0}".format(self.tag)

    @cached_property
    def title(self):
        tag_obj = Team.objects.get(name=self.tag)

        if hasattr(self, "subtag"):
            subtag_obj = Team.objects.get(name=self.subtag)
            return "{0} / {1}".format(tag_obj.title, subtag_obj.title)
        else:
            return tag_obj.title

    @classmethod
    def get(klass, *args, **kwargs):
        tag = kwargs.get("tag", None)
        subtag = kwargs.get("subtag", None)
        klass_subtag = getattr(klass, "subtag", None)

        if tag and klass.tag == tag.lower():
            if subtag and hasattr(klass, "subtag"):
                if klass_subtag == subtag.lower():
                    return klass
            else:
                return klass

    def get_queryset(self):
        filter_kwargs = dict(tagging__archived=False)
        if hasattr(self, "subtag"):
            filter_kwargs["tagging__team__name"] = self.subtag
        else:
            filter_kwargs["tagging__team__name"] = self.tag
        return Episode.objects.filter(**filter_kwargs)

    def visibile_to_user(self):
        return not self.__class__.__name__ == "TaggedPatientList"
