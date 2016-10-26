"""
OPAL PLugin - base class and helpers
"""
import inspect
import os
from django.conf import settings
from opal.utils import _itersubclasses


class OpalPlugin(object):
    """
    Base class from which all of our plugins inherit.
    """
    urls        = []
    javascripts = []
    apis        = []
    stylesheets = []
    menuitems   = []
    actions     = []
    head_extra  = []
    angular_module_deps = []

    def flows(self):
        """
        Return any extra flows our plugin may hav.e
        """
        return {}

    def roles(self, user):
        """
        Given a USER, return a list of extra roles that this user has.
        """
        return {}

    @classmethod
    def directory(cls):
        """
        Give the plugins directory
        """
        return os.path.realpath(os.path.dirname(inspect.getfile(cls)))


REGISTRY = set()
AUTODISCOVERED = False

def register(what):
    #print 'registering', what
    REGISTRY.add(what)

def autodiscover():
    from opal.utils import stringport
    global AUTODISCOVERED

    for a in settings.INSTALLED_APPS:
        stringport(a)
    AUTODISCOVERED = True

    return REGISTRY

def plugins():
    """
    Generator function for plugin instances
    """
    global AUTODISCOVERED

    if not AUTODISCOVERED:
        autodiscover()
    for m in REGISTRY:
        yield m
