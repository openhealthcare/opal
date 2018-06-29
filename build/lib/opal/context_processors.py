"""
Context Processors for Opal
"""
from django.conf import settings as s
from django.utils.functional import SimpleLazyObject

from opal.core.subrecords import subrecords as subrecords_iterator


class ModelContextProcessor(object):
    def __init__(self):
        for i in subrecords_iterator():
            setattr(self, i.__name__, i)


def settings(request):
    """
    Put all settings in locals() for our templte context.
    """
    return {x: getattr(s, x) for x in dir(s)}


def models(request):
    return {
        "models": SimpleLazyObject(ModelContextProcessor)
    }
