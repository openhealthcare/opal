from django.conf import settings
from opal.utils import _itersubclasses, stringport

# So we only do it once
IMPORTED_FROM_APPS = set()


def import_from_apps(module):
    """
    Iterate through installed apps attempting to import app.wardrounds
    This way we allow our implementation, or plugins, to define their
    own ward rounds.
    """
    if not module in IMPORTED_FROM_APPS:
        for app in settings.INSTALLED_APPS:
            try:
                stringport('{0}.{1}'.format(app, module))
            except ImportError:
                pass # not a problem
        global IMPORTED_FROM_APPS
        IMPORTED_FROM_APPS.add(module)
        return


def get_subclass(module, klass):
    import_from_apps(module)
    return _itersubclasses(klass)
