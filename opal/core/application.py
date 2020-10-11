"""
Application helpers for Opal
"""
import inspect
import itertools
import os
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from opal.core import plugins, menus


class OpalApplication(object):
    core_javascripts = {
        'opal.upstream.deps': [
            "js/lib/modernizr.js",
            "js/lib/jquery-1.11.3/jquery-1.11.3.js",
            "js/lib/d3/d3.js",
            "js/lib/c3-0.4.10/c3.js",

            "js/lib/bower_components/angular/angular.js",
            "js/lib/bower_components/angular-route/angular-route.js",
            "js/lib/bower_components/angular-resource/angular-resource.js",
            "js/lib/bower_components/angular-cookies/angular-cookies.js",

            "js/lib/angular-ui-utils-0.1.0/ui-utils.js",
            "js/lib/ui-bootstrap-tpls-0.14.3.js",

            "js/lib/utils/clipboard.js",
            "bootstrap-3.1.0/js/bootstrap.js",
            "js/lib/angulartics-0.17.2/angulartics.min.js",
            "js/lib/angulartics-0.17.2/angulartics-ga.min.js",

            # "js/ui-select/dist/select.js",
            "js/lib/bower_components/angular-ui-select/dist/select.js",
            "js/lib/bower_components/ng-idle/angular-idle.js",
            "js/lib/bower_components/angular-local-storage/dist/angular-local-storage.js",  # noqa: E501
            "js/lib/bower_components/angular-growl-v2/build/angular-growl.js",
            "js/lib/jquery-plugins/idle-timer.js",
            "js/lib/jquery-plugins/jquery.stickytableheaders.js",
            "js/lib/utils/underscore.js",
            "js/lib/utils/showdown.js",
            "js/lib/utils/moment.js",
            "js/lib/ngprogress-lite/ngprogress-lite.js",
        ],
        'opal.utils': [
            "js/opal/utils.js",
            "js/opal/opaldown.js",
            "js/opal/directives.js",
            "js/opal/filters.js",
        ],
        'opal.services': [
            "js/opal/services_module.js",
            "js/opal/services/user_profile.js",
            "js/opal/services/user.js",
            "js/opal/services/item.js",
            "js/opal/services/http_interceptors.js",
            "js/opal/services/episode.js",
            "js/opal/services/patient.js",
            "js/opal/services/episode_visibility.js",
            "js/opal/services/episode_loader.js",
            "js/opal/services/record_loader.js",
            "js/opal/services/patient_loader.js",
            "js/opal/services/episode_resource.js",
            "js/opal/services/record_editor.js",
            "js/opal/services/patientlist_loader.js",
            'js/opal/services/fields_translator.js',
            'js/opal/services/referencedata.js',
            'js/opal/services/metadata.js',
            'js/opal/services/patient_consultation_record.js',
        ],
        'opal.controllers': [
            "js/opal/controllers_module.js",
            "js/opal/controllers/patient_list_redirect.js",
            "js/opal/controllers/patient_list.js",
            "js/opal/controllers/patient_detail.js",
            "js/opal/controllers/edit_item.js",
            "js/opal/controllers/edit_teams.js",
            "js/opal/controllers/delete_item_confirmation.js",
            "js/opal/controllers/keyboard_shortcuts.js",
            "js/opal/controllers/patient_access_log.js",
            "js/opal/controllers/lookup_list_reference.js"
        ]
    }
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
    default_episode_category = 'Inpatient'

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
            href=reverse(logout_view), icon="fa-sign-out", index=1000
        )
        admin = menus.MenuItem(
            href="/admin/", icon="fa-cogs", display=_("Admin"),
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
