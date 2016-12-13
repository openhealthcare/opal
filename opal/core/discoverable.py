"""
OPAL utilities for discoverable functionality
"""
import collections
import inspect

from django.conf import settings

from opal.core import exceptions
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


class DiscoverableMeta(type):
    def __new__(cls, name, bases, dct):
        newfeature = type.__new__(cls, name, bases, dct)
        newfeature.is_valid()
        return newfeature


class DiscoverableFeature(object):
    """
    Base discoverable feature providing common patterns for
    re-usable features.
    """
    __metaclass__ = DiscoverableMeta
    module_name = None
    display_name = None
    slug = None

    @classmethod
    def is_valid(klass): pass

    @classmethod
    def get_slug(klass):
        if klass.slug is not None:
            return klass.slug
        if klass.display_name is None:
            raise ValueError('Must set display_name or slug for {0}'.format(klass))
        return camelcase_to_underscore(klass.display_name).replace(' ', '')

    @classmethod
    def list(klass):
        """
        Return an iterable of subclasses of this class.
        """
        if klass.module_name is None:
            raise ValueError('Must set {0}.module_name for {0}'.format(klass))

        # We don't want to list() invalid features that have been suppressed
        def valid_generator():
            for k in get_subclass(klass.module_name, klass):
                try:
                    k.is_valid()
                    yield k
                except exceptions.InvalidDiscoverableFeatureError:
                    continue # Just don't list() it
        return valid_generator()

    @classmethod
    def get(klass, name):
        """
        Return a specific subclass by slug
        """
        for sub in klass.list():
            if sub.get_slug() == name:
                return sub
        raise ValueError('No {0} implementation with slug {1}'.format(klass, name))


sortable_orders = collections.defaultdict(set)

class SortableFeature(object):
    module_name = None

    @classmethod
    def is_valid(klass):
        order = getattr(klass, 'order', None)
        if order is None:
            return

        parents = tuple(k for k in inspect.getmro(klass) if k != klass)
        if order in sortable_orders[parents]:
            msg = "{0} is not the first subclass of {1} to be ordered {2}".format(
                str(klass), str(parents), order
            )
            raise exceptions.InvalidDiscoverableFeatureError(msg)
        sortable_orders[parents].add(order)
        return True

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
