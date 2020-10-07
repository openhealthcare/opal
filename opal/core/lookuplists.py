"""
Opal Lookuplists
"""
import logging

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.db import models

from opal import utils
from opal.core import exceptions


def get_or_create_lookuplist_item(model, name, code, system):
    """
    Given a lookuplist MODEL, the NAME of an entry, and possibly
    the associated CODE and SYSTEM pair, return an instance.

    If a preexisting uncoded entry with this name/display value
    exists, treat this as an opportunity to code it.

    If there is a preexisting entry with this code which has a
    different name/display value, raise an exception as we can't
    guess the correct thing to do in that scenario.
    """
    try:
        instance = model.objects.get(name=name, code=code, system=system)
        return instance, False
    except model.DoesNotExist:
        if code is not None and system is not None:
            if model.objects.filter(code=code, system=system).count() > 0:
                msg = 'Tried to create a lookuplist item with value {0} '
                msg += 'and code {1} but this code already exists with '
                msg += 'value {2} and code {3}'
                existing = model.objects.get(code=code, system=system)
                msg = msg.format(name, code, existing.name, existing.code)
                raise exceptions.InvalidDataError(msg)

        try:
            instance = model.objects.get(name=name)
            instance.code = code
            instance.system = system
            instance.save()
            return instance, False
        except model.DoesNotExist:
            instance = model(name=name, code=code, system=system)
            instance.save()
            return instance, True


def load_lookuplist_item(model, item):
    """
    Load an individual lookuplist item into the database

    Takes a Lookuplist instance and a dictionary in our
    expected lookuplist data structure
    """
    from opal.models import Synonym

    name = item.get('name', None)
    if name is None:
        raise exceptions.InvalidDataError(
            'Lookuplist entries must have a name'
        )

    code, system = None, None
    if item.get('coding', None):
        try:
            code   = item['coding']['code']
            system = item['coding']['system']
        except KeyError:
            msg = """
Coding entries in lookuplists must contain both `coding` and `system` values
The following lookuplist item was missing one or both values:
{0}
""".format(str(item))
            raise exceptions.InvalidDataError(msg)

    instance, created = get_or_create_lookuplist_item(
        model, name, code, system
    )

    # Handle user visible synonyms
    synonyms_created = 0
    content_type = ContentType.objects.get_for_model(model)
    for synonym in item.get('synonyms', []):
        syn, created_synonym = Synonym.objects.get_or_create(
            content_type=content_type,
            object_id=instance.id,
            name=synonym
        )
        if created_synonym:
            synonyms_created += 1

    return int(created), synonyms_created


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
    # For the purposes of FHIR CodeableConcept, .name is .display
    # We keep it as .name for Opal backwards compatibility
    name          = models.CharField(
        max_length=255, unique=True, verbose_name=_("Name")
    )
    synonyms      = GenericRelation('opal.Synonym', verbose_name=_("Synonym"))
    system        = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("System")
    )
    code          = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("Code")
    )
    # We don't particularly use .version in the current implementation, but we
    # include here for the sake of FHIR CodeableConcept compatibility
    version       = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("Version")
    )

    class Meta:
        ordering = ['name']
        abstract = True
        unique_together = ('code', 'system')

    def __str__(self):
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


def lookuplists():
    """
    Generator function for lookuplists
    """
    for lookuplist in utils._itersubclasses(LookupList):
        if not lookuplist._meta.abstract:
            yield lookuplist


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

    for model in lookuplists():
        name = model.get_api_name()
        if name in data:
            logging.info('Loading {0}'.format(name))
            num += 1

            for item in data[name]:
                created, synonyms_created = load_lookuplist_item(model, item)
                total_created += created
                total_synonyms_created += synonyms_created

    return num, total_created, total_synonyms_created
