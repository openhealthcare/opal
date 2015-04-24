"""
OPAL core collaborative Plugin
"""
from opal.core.plugins import OpalPlugin

from opal.core.collaborative import urls

class CollaborativePlugin(OpalPlugin):
    """
    Plugin entrypoint for OPAL's collaborative realtime editing features
    """
    urls = urls.urlpatterns
    javascripts = {
        'opal.upstream.deps': [
            'js/collaborative/phoenix.js',
            ],
        'opal.services': [
            'js/collaborative/collaborator.js'
        ]
    }
