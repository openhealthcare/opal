"""
Application helpers for OPAL
"""
from opal.utils import stringport


class OpalApplication(object):
    schema_module = None
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
            "js/lib/ui-bootstrap-tpls-0.11.0.js",
            "js/lib/utils/clipboard.js",
            "bootstrap-3.1.0/js/bootstrap.js",
            "js/lib/angular-strap-2.3.1/modules/compiler.js",
            "js/lib/angular-strap-2.3.1/modules/tooltip.js",
            "js/lib/angular-strap-2.3.1/modules/tooltip.tpl.js",
            "js/lib/angular-strap-2.3.1/modules/popover.js",
            "js/lib/angular-strap-2.3.1/modules/popover.tpl.js",
            "js/lib/angular-strap-2.3.1/modules/dimensions.js",
            "js/lib/angular-strap-2.3.1/modules/parse-options.js",
            "js/lib/angular-strap-2.3.1/modules/date-parser.js",
            "js/lib/angular-strap-2.3.1/modules/date-formatter.js",
            "js/lib/angular-strap-2.3.1/modules/datepicker.js",
            "js/lib/angular-strap-2.3.1/modules/datepicker.tpl.js",
            "js/lib/angular-strap-2.3.1/modules/timepicker.js",
            "js/lib/angular-strap-2.3.1/modules/timepicker.tpl.js",
            "js/lib/angular-strap-2.3.1/modules/typeahead.js",
            "js/lib/angular-strap-2.3.1/modules/typeahead.tpl.js",

            "js/lib/angulartics-0.17.2/angulartics.min.js",
            "js/lib/angulartics-0.17.2/angulartics-ga.min.js",

            "js/lib/bower_components/ment.io/dist/mentio.js",
            "js/lib/bower_components/ment.io/dist/templates.js",
            # "js/ui-select/dist/select.js",
            "js/lib/bower_components/angular-ui-select/dist/select.js",
            "js/lib/bower_components/angular-local-storage/dist/angular-local-storage.js",
            "js/lib/bower_components/ment.io/dist/templates.js",
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
            "js/opal/services/flow.js",
            "js/opal/services/user_profile.js",
            "js/opal/services/item.js",
            "js/opal/services/episode.js",
            "js/opal/services/episode_visibility.js",
            "js/opal/services/episode_loader.js",
            "js/opal/services/patient_summary.js",
            "js/opal/services/record_loader.js",
            "js/opal/services/extract_schema_loader.js",
            "js/opal/services/schema.js",
            "js/opal/services/options.js",
            "js/opal/services/patient_loader.js",
            "js/opal/services/episode_resource.js",
            "js/opal/services/record_editor.js",
            "js/opal/services/copy_to_category.js",
            "js/opal/services/patientlist_loader.js",
            'js/opal/services/fields_translater.js',
            'js/opal/services/referencedata.js',
            'js/opal/services/metadata.js',
            'js/opal/services/patient_consultation_record.js',
            "js/search/services/paginator.js",
            "js/search/templates/search_result.js",
        ],
        'opal.controllers': [
            "js/opal/controllers_module.js",
            "js/opal/controllers/patient_list_redirect.js",
            "js/opal/controllers/patient_list.js",
            "js/opal/controllers/patient_detail.js",
            "js/opal/controllers/hospital_number.js",
            "js/opal/controllers/add_episode.js",
            "js/opal/controllers/reopen_episode.js",
            "js/opal/controllers/edit_item.js",
            "js/opal/controllers/edit_teams.js",
            "js/opal/controllers/delete_item_confirmation.js",
            "js/opal/controllers/account.js",
            "js/opal/controllers/undischarge.js",
            "js/opal/controllers/copy_to_category.js",
            "js/opal/controllers/keyboard_shortcuts.js",
            "js/opal/controllers/patient_access_log.js"
        ]
    }
    javascripts   = []
    styles        = []
    actions       = []
    menuitems     = []
    default_episode_category = 'Inpatient'

    opal_angular_exclude_tracking_qs = [
        "/search",
        "/extract",
    ]

    @classmethod
    def get_core_javascripts(klass, namespace):
        """
        Return core javascripts for a given NAMESPACE
        """
        return klass.core_javascripts[namespace]

    @classmethod
    def get_javascripts(klass):
        """
        Return the javascripts for our application
        """
        return klass.javascripts

    @classmethod
    def get_menu_items(klass):
        """
        Default implementation of get_menu_items()

        By default we just return the menuitems property of the application,
        which is itself set to [] by default.
        """
        return klass.menuitems

    @classmethod
    def get_styles(klass):
        """
        Return the stylesheets for our application
        """
        return klass.styles



def get_app():
    """
    Return the current Opal Application
    """
    return OpalApplication.__subclasses__()[0]
