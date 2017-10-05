"""
Dummy OPAL application for running standalone tests
"""
from __future__ import unicode_literals

from opal.core import application

class Application(application.OpalApplication):
    pass

list_schemas = {
    'default': []
}
