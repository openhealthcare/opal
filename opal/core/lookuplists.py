"""
OPAL Lookuplists
"""
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

# class LookupList(models.Model):
#     class Meta:
#         abstract = True


class LookupList(models.Model):
    name = models.CharField(max_length=255, unique=True)
    synonyms = GenericRelation('opal.Synonym')

    class Meta:
        ordering = ['name']
        abstract = True

    def __unicode__(self):
        return self.name

    def to_dict(self, user):
        return self.name


# def lookup_list(name, module=__name__):
#     """
#     Given the name of a lookup list, return the tuple of class_name, bases, attrs
#     for the user to define the class
#     """
#     prefix = 'Lookup List: '
#     class_name = name.capitalize() # TODO handle camelcase properly
#     bases = (LookupList,)
#     attrs = {
#         'name': models.CharField(max_length=255, unique=True),
#         'synonyms': generic.GenericRelation('opal.Synonym'),
#         'Meta': type('Meta', (object,), {'ordering': ['name'],
#                                          'verbose_name': prefix+name}),
#         '__unicode__': lambda self: self.name,
#         '__module__': module,
#     }
#     return class_name, bases, attrs
