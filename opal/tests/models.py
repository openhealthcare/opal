"""
Models for just our tests
"""
from django.db import models as dmodels

from opal.core import fields
from opal import models
from opal.core import lookuplists


class Hat(lookuplists.LookupList):
    pass


class HatWearer(models.EpisodeSubrecord):
    name = dmodels.CharField(max_length=200)
    hats = dmodels.ManyToManyField(Hat, related_name="hat_wearers")


class Dog(lookuplists.LookupList):
    pass


class DogOwner(models.EpisodeSubrecord):
    name = dmodels.CharField(max_length=200)
    dog = fields.ForeignKeyOrFreeText(Dog)


class Colour(models.EpisodeSubrecord):
    _advanced_searchable = False

    name = dmodels.CharField(max_length=200)


class PatientColour(models.PatientSubrecord):
    name = dmodels.CharField(max_length=200)


class FamousLastWords(models.PatientSubrecord):
    _is_singleton = True

    words = dmodels.CharField(max_length=200, blank=True, null=True)


class EpisodeName(models.EpisodeSubrecord):
    _is_singleton = True

    name = dmodels.CharField(max_length=200, blank=True, null=True)

# We shouldn't, but we basically insist on some non-core models being there.
if not getattr(models.Patient, 'demographics_set', None):

    class Demographics(models.PatientSubrecord):
        _is_singleton = True

        hospital_number = dmodels.CharField(max_length=200, blank=True, null=True)
        name = dmodels.CharField(max_length=200, blank=True, null=True)
        date_of_birth = dmodels.DateField(blank=True, null=True)
        gender = fields.ForeignKeyOrFreeText(models.Gender)

        pid_fields = 'name',
