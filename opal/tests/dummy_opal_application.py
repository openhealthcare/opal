"""
Dummy OPAL application for running standalone tests
"""
from opal.core import application

class Application(application.OpalApplication):
    schema_module = 'opal.tests.dummy_opal_application'

list_schemas = {
    'default': []
}


