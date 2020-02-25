"""
Plugin definition for the pathway Opal plugin
"""
from opal.core import plugins
from opal.core.pathway.urls import urlpatterns


class PathwayPlugin(plugins.OpalPlugin):
    """
    Main entrypoint to expose this plugin to our OPAL application.
    """
    urls = urlpatterns

    javascripts = {
        # Add your javascripts here!
        'opal.services': [
            'js/pathway/services/pathway.js',
            'js/pathway/services/wizard_pathway.js',
            'js/pathway/services/pathway_loader.js',
        ],
        'opal.controllers': [
            'js/pathway/app.js',
            'js/pathway/controllers/pathway_redirect.js',
            'js/pathway/controllers/default_step.js',
            'js/pathway/controllers/default_single_step.js',
            'js/pathway/controllers/pathway_ctrl.js',
            'js/pathway/controllers/modal_pathway_ctrl.js',
            'js/pathway/directives.js',
        ]
    }
