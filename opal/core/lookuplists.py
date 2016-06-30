"""
OPAL Lookuplists
"""
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models


def synonym_exists(lookuplist, name):
    """
        A lookup list name should be uniqe among its
        type and synonyms of its type
    """
    from opal.models import Synonym
    ct = ContentType.objects.get_for_model(lookuplist)
    return Synonym.objects.filter(
        content_type=ct, name=name
    ).exists()


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

    def save(self, *args, **kwargs):
        """ Save the lookuplist value, but do a check that makes
            sure there isn't a synonym already with this name for
            this ct
        """
        if synonym_exists(self.__class__, self.name):
            err_str = "{0}, or a synonym of one, already exists with the name {1}"
            class_name = self.__class__.__name__
            raise ValueError(err_str.format(class_name, self.name))
        return super(LookupList, self).save(*args, **kwargs)
