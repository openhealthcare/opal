"""
Opal Plugin - base class and helpers
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
        return [u for u in klass.urls]

    @classmethod
    def get_apis(klass):
        """
        Return the apis
        """
        return [a for a in klass.apis]

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

    @classmethod
    def get_styles(klass):
        """
        Return the stylesheets for our plugin
        """
        return [s for s in klass.stylesheets]

    @classmethod
    def get_javascripts(klass):
        """
        Return the javascripts for our plugin
        """
        return [j for j in klass.javascripts]

    @classmethod
    def get_menu_items(cls, user=None):
        return [i for i in cls.menuitems if i.for_user(user)]
