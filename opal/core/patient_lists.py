from opal.models import Episode
from opal.core import app_importer


class PatientList(object):
    """
    A view of a list shown on the list page, complete with schema that
    define the columns shown and a queryset that defines the episodes shown
    """
    def __init__(self, request, *args, **kwargs):
        self.request = request

    @property
    def schema(self):
        raise "this needs to be implemented"

    @property
    def queryset(self):
        raise "this needs to be implemented"

    def get_queryset(self):
        return self.queryset

    def get_serialised(self):
        # only bringing in active seems a sensible default at this time
        return self.get_queryset().serialised_active(self.request.user)

    @classmethod
    def list_classes(klass):
        return app_importer.get_subclass("patient_lists", klass)

    @classmethod
    def get_class(klass, request, **kwargs):
        list_classes = klass.list_classes()
        for list_class in list_classes:
            lc = list_class.get(**kwargs)
            if lc:
                return lc(request)


class TaggedPatientList(PatientList):
    """
    The most common list use case of a patient list, when we define a tag
    and a sub tag and look up the episodes on the basis of these. You still
    need to define schema
    """
    tag = "Implement me please"

    @classmethod
    def get(klass, **kwargs):
        tag = kwargs.get("tag", None)
        subtag = kwargs.get("subtag", None)
        klass_subtag = getattr(klass, "subtag", None)

        if tag and klass.tag == tag.lower():
            if not klass_subtag or klass_subtag == subtag.lower():
                return klass

    def get_queryset(self):
        filter_kwargs = dict(tagging__archived=False)
        if getattr(self, "subtag", None):
            filter_kwargs["tagging__team__name"] = self.subtag
        else:
            filter_kwargs["tagging__team__name"] = self.tag
        return Episode.objects.filter(**filter_kwargs)
