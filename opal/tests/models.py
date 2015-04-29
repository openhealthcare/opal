"""
Models for just our tests
"""
from django.db import models as dmodels
from opal import models

class Colour(models.EpisodeSubrecord):
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

        pid_fields = 'name',
