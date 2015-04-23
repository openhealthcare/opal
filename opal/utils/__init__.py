"""
Generic OPAL utilities
"""
import importlib
import re

camelcase_to_underscore = lambda str: re.sub('(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))', '_\\1', str).lower().strip('_')

def stringport(module):
    """
    Given a string representing a python module or path-to-object 
    import that module and return it.
    """
    msg = "Could not import module '%s'\
                   (Is it on sys.path? Does it have syntax errors?)" % module
    try:
        return importlib.import_module(module)
    except ImportError, e:
        try:
            module, obj = module.rsplit('.', 1)
            module = importlib.import_module(module)
            if hasattr(module, obj):
                return getattr(module, obj)
            else:
                raise ImportError(msg + e.message)
        except ImportError, e:
            raise ImportError(msg + e.message)
        raise ImportError(msg + e.message)


