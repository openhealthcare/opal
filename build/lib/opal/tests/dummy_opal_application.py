"""
Dummy OPAL application for running standalone tests
"""
from opal.core import application

class Application(application.OpalApplication):
    pass

list_schemas = {
    'default': []
}
