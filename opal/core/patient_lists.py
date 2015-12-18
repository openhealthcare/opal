from django.conf import settings

from opal.utils import _itersubclasses
from opal.utils import stringport
from opal.models import Episode

# So we only do it once
IMPORTED_FROM_APPS = False


def import_from_apps():
    """
    Iterate through installed apps attempting to import app.wardrounds
    This way we allow our implementation, or plugins, to define their
    own ward rounds.
    """
    for app in settings.INSTALLED_APPS:
        try:
            stringport(app + '.patient_lists')
            print "successfully imported %s" % app
        except ImportError:
            pass # not a problem
    global IMPORTED_FROM_APPS
    IMPORTED_FROM_APPS = True
    return


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
        if not IMPORTED_FROM_APPS:
            import_from_apps()
        return _itersubclasses(PatientList)

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
