"""
OPAL Lookuplists
"""
import logging

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models


def load_lookuplist_item(model, item):
    from opal.models import Synonym
    content_type = ContentType.objects.get_for_model(model)
    instance, created = model.objects.get_or_create(name=item['name'])
    synonyms_created = 0

    for synonym in item['synonyms']:
        syn, created_synonym = Synonym.objects.get_or_create(
            content_type=content_type,
            object_id=instance.id,
            name=synonym
        )
        if created_synonym:
            synonyms_created += 1
    return int(created), synonyms_created


def load_lookuplist(data):
    """
        returns num, total_created, total_synonyms_created
        where
        num is the number of lookup lists models we look at
        created is the number of instances of lookup list created
        synonym is the total number of synonyms created
    """
    num = 0
    total_created = 0
    total_synonyms_created = 0

    for model in LookupList.__subclasses__():
        name = model.__name__.lower()
        if name in data:
            logging.info('Loading {0}'.format(name))
            num += 1

            for item in data[name]:
                created, synonyms_created = load_lookuplist_item(model, item)
                total_created += created
                total_synonyms_created += synonyms_created

    return num, total_created, total_synonyms_created


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
            err_str = "{0}, or a synonym of one, already exists with the " \
                      "name {1}"
            class_name = self.__class__.__name__
            raise ValueError(err_str.format(class_name, self.name))
        return super(LookupList, self).save(*args, **kwargs)
