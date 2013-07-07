from django.db import models
from records.models import PatientSubrecord, AdmissionSubrecord

class Demographics(PatientSubrecord):
    name = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True)

class Location(AdmissionSubrecord):
    ward = models.CharField(max_length=255, blank=True)
    bed = models.CharField(max_length=255, blank=True)
