"""
Generic Opal utilities
"""
import importlib
import re
import sys

from django.template import TemplateDoesNotExist
from django.template.loader import select_template


def camelcase_to_underscore(string):
    return re.sub(
        '(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))', '_\\1', string
    ).lower().strip('_')


class AbstractBase(object):
    """
    This placeholder class allows us to filter out abstract
    bases when iterating through subclasses.
    """


def stringport(module):
    """
    Given a string representing a python module or path-to-object
    import that module and return it.
    """
    try:
        return importlib.import_module(module)
    except ImportError:
        try:
            if '.' not in module:
                raise
            module, obj = module.rsplit('.', 1)
            module = importlib.import_module(module)
            if hasattr(module, obj):
                return getattr(module, obj)
            else:
                raise
        except ImportError:
            raise


def _itersubclasses(cls, _seen=None):
    """
    Recursively iterate through subclasses
    """
    abstract_classes = AbstractBase.__subclasses__()

    if _seen is None:
        _seen = set()
    try:
        subs = cls.__subclasses__()
    except TypeError:  # fails only when cls is type
        subs = cls.__subclasses__(cls)
    for sub in subs:
        if sub not in _seen:
            _seen.add(sub)
            if sub not in abstract_classes:
                yield sub
            for sub in _itersubclasses(sub, _seen):
                if sub not in abstract_classes:
                    yield sub


def find_template(template_list):
    """
    Given an iterable of template paths, return the first one that
    exists on our template path or None.
    """
    try:
        return select_template(template_list).template.name
    except TemplateDoesNotExist:
        return None


def write(what):
    """
    Writes the argument to `sys.stdout` unless it detects an active test run.
    If run during tests, it should do nothing.
    """
    if 'runtests.py' in sys.argv:
        return
    sys.stdout.write("{0}\n".format(what))
