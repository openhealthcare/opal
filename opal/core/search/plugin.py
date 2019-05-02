"""
Plugin definition for opal.core.search
"""
from opal.core.search import api, urls
from opal.core import plugins


class SearchPlugin(plugins.OpalPlugin):
    """
    The plugin entrypoint for Opal's core search functionality
    """
    urls = urls.urlpatterns
    stylesheets = ["css/search.css"]
    javascripts = {
        'opal.services': [
            'js/search/services/filter.js',
            'js/search/services/extract_schema.js',
            'js/search/services/extract_schema_loader.js',
            'js/search/services/filters_loader.js',
            'js/search/services/filter_resource.js',
            "js/search/services/paginator.js",
            "js/search/services/patient_summary.js",
        ],
        'opal.controllers': [
            'js/search/app.js',
            'js/search/controllers/search.js',
            'js/search/controllers/extract.js',
            "js/search/controllers/save_filter.js",
        ]
    }

    apis = [
        ('extract-schema', api.ExtractSchemaViewSet)
    ]

    opal_angular_exclude_tracking_prefix = [
        "/search",
        "/extract",
    ]
