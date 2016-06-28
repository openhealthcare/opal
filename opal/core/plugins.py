"""
OPAL PLugin - base class and helpers
"""
import inspect
import os

from opal.core import discoverable


class OpalPlugin(discoverable.DiscoverableFeature):
    """
    Base class from which all of our plugins inherit.
    """
    module_name = 'plugin'

    urls        = []
    javascripts = []
    apis        = []
    stylesheets = []
    menuitems   = []
    actions     = []
    head_extra  = []
    angular_module_deps = []

    @classmethod
    def get_urls(klass):
        """
        Return the urls
        """
        return klass.urls

    @classmethod
    def get_apis(klass):
        """
        Return the apis
        """
        return klass.apis

    @classmethod
    def directory(cls):
        """
        Give the plugins directory
        """
        return os.path.realpath(os.path.dirname(inspect.getfile(cls)))

    def flows(self):
        """
        Return any extra flows our plugin may have.
        """
        return {}

    def roles(self, user):
        """
        Given a USER, return a list of extra roles that this user has.
        """
        return {}


# These two are only here for legacy reasons.
# TODO: Consider removing and updating elsewhere.
def register(what):
    pass

def plugins():
    """
    Generator function for plugin instances
    """
    return OpalPlugin.list()
