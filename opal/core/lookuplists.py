"""
OPAL Lookuplists
"""
from django.contrib.contenttypes import generic
from django.db import models

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
