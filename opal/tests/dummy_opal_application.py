"""
Dummy OPAL application for running standalone tests
"""
from opal.core import application

class Application(application.OpalApplication):
    default_episode_category = 'Inpatient'
    pass

list_schemas = {
    'default': []
}
