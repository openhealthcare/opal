"""
Opal utilities for discoverable functionality
"""
from django.conf import settings
from six import with_metaclass

from opal.core import exceptions
from opal.utils import (
    camelcase_to_underscore, _itersubclasses, stringport, AbstractBase
)

# So we only do it once
IMPORTED_FROM_APPS = set()


def import_from_apps(module):
    """
    Iterate through installed apps attempting to import app.wardrounds
    This way we allow our implementation, or plugins, to define their
    own ward rounds.
    """
    global IMPORTED_FROM_APPS
    if module not in IMPORTED_FROM_APPS:
        for app in settings.INSTALLED_APPS:
            try:
                stringport('{0}.{1}'.format(app, module))
            except ImportError:
                pass  # not a problem
        IMPORTED_FROM_APPS.add(module)
        return


def get_subclass(module, klass):
    import_from_apps(module)
    return _itersubclasses(klass)


class DiscoverableManager(object):

    def all(self):
        return list(get_subclass(self.feature.module_name, self.feature))

    def filter(self, *args, **kwargs):
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
                    raise ValueError(msg.format(self.feature, attribute))
                if getattr(feature, attribute) != kwargs[attribute]:
                    match = False
            return match

        return [f for f in self.all() if feature_filter(f)]

    def get(self, *args, **kwargs):
        """
        Return a single instance of a feature based on a Django Queryset-like
        interface.
        """
        matches = self.filter(*args, **kwargs)
        if len(matches) > 1:
            raise ValueError("More than one matching {0} for {1}".format(
                str(self.feature), str(kwargs)
            ))
        if len(matches) == 0:
            raise ValueError("No matching {0} for {1}".format(
                str(self.feature), str(kwargs)
            ))
        return matches[0]


class DiscoverableMeta(type):

    def __new__(cls, name, bases, attrs):
        newfeature = type.__new__(cls, name, bases, attrs)
        newfeature.is_valid()
        if 'implementations' in attrs:
            if not isinstance(attrs['implementations'], DiscoverableManager):
                msg = "DiscoverableFeature.implementations must be a " \
                      "DiscoverableManager subclass"
                raise ValueError(msg)
            else:
                newfeature.implementations.feature = newfeature
        else:
            klassstr = "<class 'opal.core.discoverable.DiscoverableFeature'>"
            should_have_manager = False
            if klassstr in [str(c) for c in bases]:
                should_have_manager = True
            if AbstractBase in bases:
                should_have_manager = True

            if should_have_manager:
                newfeature.implementations = DiscoverableManager()
                newfeature.implementations.feature = newfeature
            else:
                if name != 'DiscoverableFeature':
                    if hasattr(newfeature, 'implementations'):
                        newfeature.implementations = None
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


class SortableFeature(object):
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
