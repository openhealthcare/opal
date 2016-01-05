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
        if not IMPORTED_FROM_APPS:
            import_from_apps()
        return _itersubclasses(PatientList)

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
    subtag = "Implement me please"

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
    """
    if the user has tagged episodes as their's this will give them the appropriate
    episode queryset
    """
    @classmethod
    def get(klass, **kwargs):
        tag = kwargs.get("tag", None)
        if tag and "mine" == tag.lower():
            return klass

    def get_queryset(self):
        return Episode.objects.filter(tagging__user=self.request.user)
