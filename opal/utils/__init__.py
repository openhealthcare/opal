"""
Generic OPAL utilities
"""
import importlib
import os
import re

from django.template import engines, TemplateDoesNotExist

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
            if '.' not in module:
                raise
            module, obj = module.rsplit('.', 1)
            module = importlib.import_module(module)
            if hasattr(module, obj):
                return getattr(module, obj)
            else:
                raise ImportError(msg)
        except ImportError, e:
            raise ImportError(msg)
        raise ImportError(msg)


def _itersubclasses(cls, _seen=None):
    """
    Recursively iterate through subclasses
    """
    if not isinstance(cls, type):
        raise TypeError('itersubclasses must be called with '
                        'new-style classes, not %.100r' % cls)
    if _seen is None: _seen = set()
    try:
        subs = cls.__subclasses__()
    except TypeError: # fails only when cls is type
        subs = cls.__subclasses__(cls)
    for sub in subs:
        if sub not in _seen:
            _seen.add(sub)
            yield sub
            for sub in _itersubclasses(sub, _seen):
                yield sub


def find_template(template_list):
    """
    Given an iterable of template paths, return the first one that
    exists on our template path or None.
    """
    for path in template_list:
        for engine in engines.all():
            for loader in engine.engine.template_loaders:
                for origin in loader.get_template_sources(path):
                    if os.path.exists(origin):
                        return path
    return None
