"""
Application helpers for Opal
"""
import inspect
import itertools
import os

from django.urls import reverse
from opal.core import plugins, menus


class OpalApplication(object):
    core_javascripts = {}
    angular_module_deps = []
    javascripts = []
    styles = []
    actions = []
    menuitems = [
        menus.MenuItem(
            href="/#/list/", activepattern="/list/",
            icon="fa-table", display="Lists",
            index=0
        )
    ]
    default_episode_category = 'Episode'

    @classmethod
    def get_core_javascripts(klass, namespace):
        """
        Return core javascripts for a given NAMESPACE
        """
        return [x for x in klass.core_javascripts[namespace]]

    @classmethod
    def get_javascripts(klass):
        """
        Return the javascripts for our application
        """
        return [x for x in klass.javascripts]

    @classmethod
    def get_menu_items(klass, user=None):
        """
        Default implementation of get_menu_items()
        """
        # we import here as settings must be set before this is imported
        from django.contrib.auth.views import logout as logout_view
        logout = menus.MenuItem(
            href=reverse(logout_view), icon="fa-sign-out", index=1000, display="Log Out"
        )
        admin = menus.MenuItem(
            href="/admin/", icon="fa-cogs", display="Admin",
            index=999
        )
        items = []
        items += klass.menuitems
        if user:
            if not user.is_authenticated:
                return []
            else:
                items.append(logout)
                if user.is_staff:
                    items.append(admin)
        return [item for item in items if item.for_user(user)]

    @classmethod
    def get_menu(klass, user=None):
        """
        Return the Menu for this application.
        """
        return menus.Menu(user=user)

    @classmethod
    def get_styles(klass):
        """
        Return the stylesheets for our application
        """
        return [x for x in klass.styles]

    @classmethod
    def directory(cls):
        """
        Return the filesystem path to the app directory
        """
        return os.path.realpath(os.path.dirname(inspect.getfile(cls)))

    @classmethod
    def get_all_angular_module_deps(cls):
        all_angular_module_deps = []
        for i in get_all_components():
            all_angular_module_deps.extend(i.angular_module_deps)
        return all_angular_module_deps


def get_app():
    """
    Return the current Opal Application
    """
    return OpalApplication.__subclasses__()[0]


def get_all_components():
    """
    All components of an Opal application - all plugins and the application.
    """
    return itertools.chain(
        plugins.OpalPlugin.list(), [get_app()]
    )
