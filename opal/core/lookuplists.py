"""
OPAL Lookuplists
"""
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models


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

    @classmethod
    def get_api_name(cls):
        return cls.__name__.lower()
