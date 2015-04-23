"""
OPAL core search package
"""
from opal.core.search import urls

from opal.core.plugins import OpalPlugin

class SearchPlugin(OpalPlugin):
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
            'js/search/controllers/extract.js'
        ]
    }
