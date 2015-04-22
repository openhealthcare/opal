"""
Application helpers for OPAL
"""
from opal.utils import stringport

class OpalApplication(object):
    schema_module = None
    flow_module   = None
    javascripts   = []
    actions       = []
    
    default_episode_category = 'inpatient'

    @classmethod
    def flows(klass):
        """
        Default implementation of flows()

        Pulls flows defined in the application's flows module,
        plus any flows defined by plugins.
        """
        from opal.core.plugins import OpalPlugin

        flows = {}
        for plugin in OpalPlugin.__subclasses__():
            flows.update(plugin().flows())
            
        if klass.flow_module is None:
            return flows
        
        flow = stringport(klass.flow_module)
        flows.update(flow.flows)
        return flows

def get_app():
    """
    Return the current Opal Application
    """
    return OpalApplication.__subclasses__()[0]
