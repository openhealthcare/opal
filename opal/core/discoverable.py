"""
OPAL utilities for discoverable functionality
"""
from opal.core.app_importer import get_subclass
from opal.utils import camelcase_to_underscore

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
