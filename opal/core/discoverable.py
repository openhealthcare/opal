"""
Opal utilities for discoverable functionality
"""
from django.conf import settings
from six import with_metaclass

from opal.core import exceptions
from opal.utils import camelcase_to_underscore, _itersubclasses, stringport

# So we only do it once
IMPORTED_FROM_APPS = set()


def import_from_apps(module):
    """
    Iterate through installed apps attempting to import app.`module`.

    This enables us to ensure that we have autoloaded instances of
    discoverables.
    """
    global IMPORTED_FROM_APPS
    if module not in IMPORTED_FROM_APPS:
        for app in settings.INSTALLED_APPS:
            try:
                target_module = '{0}.{1}'.format(app, module)
                stringport(target_module)
            except ImportError as e:
                expected_errs = [
                    "No module named {0}".format(module),  # Python 2.x
                    "No module named '{0}'".format(target_module)  # Python 3.x
                ]
                if str(e) in expected_errs:
                    continue  # not a problem - we expect this
                raise  # a problem - probably inside the target module.
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


class DiscoverableFeature(with_metaclass(DiscoverableMeta, object)):
    """
    Base discoverable feature providing common patterns for
    re-usable features.
    """
    module_name = None
    display_name = None
    slug = None

    @classmethod
    def is_valid(klass):
        pass

    @classmethod
    def get_slug(klass):
        if klass.slug is not None:
            return klass.slug
        if klass.display_name is None:
            raise ValueError(
                'Must set display_name or slug for {0}'.format(klass)
            )
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
                    continue  # Just don't list() it
        return valid_generator()

    @classmethod
    def get(klass, name):
        """
        Return a specific subclass by slug
        """
        for sub in klass.list():
            if sub.get_slug() == name:
                return sub
        raise ValueError('No {0} implementation with slug {1}'.format(
            klass, name))

    @classmethod
    def filter(klass, *args, **kwargs):
        """
        Return all matching instances of a feature based on a Django
        Queryset-like interface.
        """
        def feature_filter(feature):
            match = True
            for attribute in kwargs:
                if not hasattr(feature, attribute):
                    msg = "Invalid Query: At least one {0} implementation " \
                          "does not have a {1} attribute."
                    raise ValueError(msg.format(klass, attribute))
                if getattr(feature, attribute) != kwargs[attribute]:
                    match = False
            return match

        return [f for f in klass.list() if feature_filter(f)]


class SortableFeature(object):
    """
    Mixin class to provide ordering for features
    """
    module_name = None

    @classmethod
    def list(klass):
        """
        Return an iterable of Patient Lists.
        """
        if klass.module_name is None:
            raise ValueError('Must set {0}.module_name for {0}'.format(klass))
        klasses = sorted(
            get_subclass(klass.module_name, klass), key=lambda x: x.order
        )
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
