"""
Dummy OPAL application for running standalone tests
"""
from opal.core import application
from opal.tests.episode_categories import InpatientEpisode

class Application(application.OpalApplication):
    default_episode_category = InpatientEpisode.display_name


list_schemas = {
    'default': []
}
