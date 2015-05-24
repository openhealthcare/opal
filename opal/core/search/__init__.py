"""
OPAL core search package
"""
from opal.core.search import urls
from opal.core import plugins

class SearchPlugin(plugins.OpalPlugin):
    """
    The plugin entrypoint for OPAL's core search functionality
    """
    urls = urls.urlpatterns
    javascripts = {
        'opal.services': [
            'js/search/services/filter.js',
            'js/search/services/filters_loader.js',
            'js/search/services/filter_resource.js'
        ],
        'opal.controllers': [
            'js/search/controllers/search.js',
            'js/search/controllers/extract.js',
            "js/search/controllers/save_filter.js",
        ]
    }

plugins.register(SearchPlugin)
