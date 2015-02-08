"""
Application helpers for OPAL
"""
class OpalApplication(object):
    schema_module = None
    flow_module   = None
    javascripts   = []
    actions       = []
    
    default_episode_category = 'inpatient'

def get_app():
    """
    Return the current Opal Application
    """
    return OpalApplication.__subclasses__()[0]
