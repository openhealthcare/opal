"""
OPAL PLugin - base class and helpers
"""
import inspect
import os
import warnings

from opal.core import discoverable

warnings.simplefilter('once', DeprecationWarning)


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

    def roles(self, user):
        """
        Given a USER, return a list of extra roles that this user has.
        """
        return {}


# TODO 0.9.0: Remove these
def register(what):
    warnthem = """

opal.core.plugins.register is no longer required and will be removed in
Opal 0.9.0

There is no need to register {0} as Plugins are now discoverable features.

Please consult the Opal documentation on Plugins for more information.
""".format(what)
    warnings.warn(warnthem, DeprecationWarning, stacklevel=2)
    pass


def plugins():
    """
    Generator function for plugin instances
    """
    warnthem = """

opal.core.plugins.plugins is slated for removal in Opal 0.9.0

Plugins are now discoverable features, an iterable of subclasses
may be accessed via

opal.core.plugins.OpalPlugin.list
"""
    warnings.warn(warnthem, DeprecationWarning, stacklevel=2)
    return OpalPlugin.list()
