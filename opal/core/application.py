"""
Application helpers for OPAL
"""
from opal.utils import stringport


class OpalApplication(object):
    schema_module = None
    core_javascripts = {
        'opal.upstream.deps': [
            "js/modernizr.js",
            "js/jquery-1.11.3/jquery-1.11.3.js",
            "js/d3/d3.js",
            "js/c3-0.4.10/c3.js",

            # "js/angular-1.2.20/angular.js",
            # "js/angular-1.2.20/angular-route.js",
            # "js/angular-1.2.20/angular-cookies.js",
            # "js/angular-1.2.20/angular-resource.js",
            "js/bower_components/angular/angular.js",
            "js/bower_components/angular-route/angular-route.js",
            "js/bower_components/angular-resource/angular-resource.js",
            "js/bower_components/angular-cookies/angular-cookies.js",

            "js/angular-ui-utils-0.1.0/ui-utils.js",
            "js/ui-bootstrap-tpls-0.11.0.js",

            "bootstrap-3.1.0/js/bootstrap.js",

            "js/angular-strap-2.3.1/modules/compiler.js",
            "js/angular-strap-2.3.1/modules/tooltip.js",
            "js/angular-strap-2.3.1/modules/tooltip.tpl.js",
            "js/angular-strap-2.3.1/modules/popover.js",
            "js/angular-strap-2.3.1/modules/popover.tpl.js",
            "js/angular-strap-2.3.1/modules/dimensions.js",
            "js/angular-strap-2.3.1/modules/parse-options.js",
            "js/angular-strap-2.3.1/modules/date-parser.js",
            "js/angular-strap-2.3.1/modules/date-formatter.js",
            "js/angular-strap-2.3.1/modules/datepicker.js",
            "js/angular-strap-2.3.1/modules/datepicker.tpl.js",
            "js/angular-strap-2.3.1/modules/timepicker.js",
            "js/angular-strap-2.3.1/modules/timepicker.tpl.js",
            "js/angular-strap-2.3.1/modules/typeahead.js",
            "js/angular-strap-2.3.1/modules/typeahead.tpl.js",

            "js/angulartics-0.17.2/angulartics.min.js",
            "js/angulartics-0.17.2/angulartics-ga.min.js",

            "js/bower_components/ment.io/dist/mentio.js",
            "js/bower_components/ment.io/dist/templates.js",
            # "js/ui-select/dist/select.js",
            "js/bower_components/angular-ui-select/dist/select.js",
            "js/bower_components/angular-local-storage/dist/angular-local-storage.js",
            "js/bower_components/ment.io/dist/templates.js",
            "js/bower_components/angular-growl-v2/build/angular-growl.js",
            "js/jquery-plugins/idle-timer.js",
            "js/jquery-plugins/jquery.stickytableheaders.js",
            "js/utils/underscore.js",
            "js/utils/showdown.js",
            "js/utils/moment.js",
            "js/ngprogress-lite/ngprogress-lite.js",
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
            "js/opal/services/episode_detail.js",
            "js/opal/services/patientlist_loader.js",
            "js/opal/services/tag_service.js",
            'js/opal/services/fields_translater.js',
            "js/search/services/paginator.js",
        ],
        'opal.controllers': [
            "js/opal/controllers_module.js",
            "js/opal/controllers/patient_list_redirect.js",
            "js/opal/controllers/patient_list.js",
            "js/opal/controllers/episode_detail.js",
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
    def get_menu_items(klass):
        """
        Default implementation of get_menu_items()

        By default we just return the menuitems property of the application,
        which is itself set to [] by default.
        """
        return klass.menuitems


def get_app():
    """
    Return the current Opal Application
    """
    return OpalApplication.__subclasses__()[0]
