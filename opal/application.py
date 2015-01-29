"""
Application helpers for OPAL
"""
class OpalApplication(object):
    schema_module = None
    flow_module   = None
    javascripts   = []
    actions       = []

def get_app():
    """
    Return the current Opal Application
    """
    return OpalApplication.__subclasses__()[0]
