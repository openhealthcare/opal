"""
OPAL utilities for discoverable functionality
"""
from django.conf import settings

from opal.utils import camelcase_to_underscore, _itersubclasses, stringport

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


class DiscoverableFeature(object):
    """
    Base discoverable feature providing common patterns for
    re-usable features.
    """
    module_name = None
    name = None

    @classmethod
    def slug(klass):
        if klass.name is None:
            raise ValueError('Must set {0}.name for {0}'.format(klass))
        return camelcase_to_underscore(klass.name).replace(' ', '')

    @classmethod
    def list(klass):
        """
        Return an iterable of subclasses of this class.
        """
        if klass.module_name is None:
            raise ValueError('Must set {0}.module_name for {0}'.format(klass))
        return get_subclass(klass.module_name, klass)

    @classmethod
    def get(klass, name):
        """
        Return a specific subclass by slug
        """
        for sub in klass.list():
            if sub.slug() == name:
                return sub
        raise ValueError('No {0} implementation with slug {1}'.format(klass, name))


class SortableFeature(object):
    module_name = None

    @classmethod
    def list(klass):
        """
        Return an iterable of Patient Lists.
        """
        if klass.module_name is None:
            raise ValueError('Must set {0}.module_name for {0}'.format(klass))
        klasses = sorted(get_subclass(klass.module_name, klass), key=lambda x: x.order)
        return klasses


class RestrictableFeature(object):

    @classmethod
    def for_user(klass, user):
        """
        Return the set of instances that this USER can see.
        """
        for k in klass.list():
            if k.visible_to(user):
                yield k

    @classmethod
    def visible_to(klass, user):
        return True
