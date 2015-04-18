"""
OPAL model utils
"""

from django.contrib.contenttypes import generic
from django.db import models

from opal.utils.fields import ForeignKeyOrFreeText

class LookupList(models.Model):
    class Meta:
        abstract = True


def lookup_list(name, module=__name__):
    """
    Given the name of a lookup list, return the tuple of class_name, bases, attrs
    for the user to define the class
    """
    prefix = 'Lookup List: '
    class_name = name.capitalize() # TODO handle camelcase properly
    bases = (LookupList,)
    attrs = {
        'name': models.CharField(max_length=255, unique=True),
        'synonyms': generic.GenericRelation('opal.Synonym'),
        'Meta': type('Meta', (object,), {'ordering': ['name'], 
                                         'verbose_name': prefix+name}),
        '__unicode__': lambda self: self.name,
        '__module__': module,
    }
    return class_name, bases, attrs
    
 
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

def episode_subrecords():
    """
    Generator function for episode subrecords.
    """
    from opal.models import EpisodeSubrecord
    for model in _itersubclasses(EpisodeSubrecord):
        if model._meta.abstract:
            continue
        yield model

def patient_subrecords():
    """
    Generator function for patient subrecords.
    """
    from opal.models import PatientSubrecord
    for model in _itersubclasses(PatientSubrecord):
        if model._meta.abstract:
            continue
        yield model

def subrecords():
    """
    Generator function for subrecords
    """
    for m in episode_subrecords():
        yield m
    for m in patient_subrecords():
        yield m
    
