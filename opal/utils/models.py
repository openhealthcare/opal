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
    class_name = name.capitalize() # TODO handle camelcase properly
    bases = (LookupList,)
    attrs = {
        'name': models.CharField(max_length=255, unique=True),
        'synonyms': generic.GenericRelation('opal.Synonym'),
        'Meta': type('Meta', (object,), {'ordering': ['name'], 
                                         'verbose_name': 'Lookup List: '+name}),
        '__unicode__': lambda self: self.name,
        '__module__': module,
    }
    return class_name, bases, attrs
    
    

# These are models for testing.
# TODO move these to tests directory so they are not made available when app is
# added to INSTALLED_APPS.


class Colour(models.Model):
    name = models.CharField(max_length=255)

class Person(models.Model):
    favorite_colour = ForeignKeyOrFreeText(Colour)
