"""
Generic OPAL utilities
"""
from collections import namedtuple
import importlib
import re

camelcase_to_underscore = lambda str: re.sub('(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))', '_\\1', str).lower().strip('_')

def stringport(module):
    try:
        return importlib.import_module(module)
    except ImportError, e:
        raise ImportError("Could not import module '%s'\
                   (Is it on sys.path? Does it have syntax errors?):\
                    %s" % (module, e))

Tag = namedtuple('Tag', 'name title subtags')
