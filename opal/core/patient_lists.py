from opal.models import Episode
from opal.core import app_importer


class PatientList(object):
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
        for list_class in klass.list_classes():
            lc = list_class.get(**kwargs)
            if lc:
                return lc(request)


class TaggedPatientList(object):
    @classmethod
    def get(klass, **kwargs):
        tag = kwargs.get("tag", None)
        subtag = kwargs.get("subtag", None)

        if tag and klass.tag == tag.lower():
            if not klass.subtag or klass.subtag == subtag.lower():
                return klass

    def get_queryset(self):
        filter_kwargs = dict(tagging__archived=False)
        if self.subtag:
            filter_kwargs["tagging__team__name"] = self.subtag
        else:
            filter_kwargs["tagging__team__name"] = self.tag
        return Episode.objects.filter(**filter_kwargs)


class Mine(PatientList):
    @classmethod
    def get(klass, **kwargs):
        tag = kwargs.get("tag", None)
        if tag and "mine" == tag.lower():
            return klass

    def get_queryset(self):
        return Episode.objects.filter(tagging_user=self.request.user)
