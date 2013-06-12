from django.db import models
from django.dispatch import receiver

from utils.fields import ForeignKeyOrFreeText
from options.models import option_models

class Patient(models.Model):
    pass

class SingletonSubrecord(models.Model):
    patient = models.OneToOneField(Patient)

    class Meta:
        abstract = True

class Subrecord(models.Model):
    patient = models.ForeignKey(Patient)

    class Meta:
        abstract = True

class Demographics(SingletonSubrecord):
    name = models.CharField(max_length=255, blank=True)
    hospital_number = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

class Location(SingletonSubrecord):
    category = models.CharField(max_length=255, blank=True)
    hospital = models.CharField(max_length=255, blank=True)
    ward = models.CharField(max_length=255, blank=True)
    bed = models.CharField(max_length=255, blank=True)
    date_of_admission = models.DateField(null=True, blank=True)

class Diagnosis(Subrecord):
    condition = ForeignKeyOrFreeText(option_models['condition'])
    provisional = models.BooleanField()
    details = models.CharField(max_length=255, blank=True)

class PastMedicalHistory(Subrecord):
    condition = ForeignKeyOrFreeText(option_models['condition'])
    year = models.CharField(max_length=4, blank=True)

class GeneralNote(Subrecord):
    date = models.DateField(null=True, blank=True)
    comment = models.TextField()

class Destination(Subrecord):
    destination = ForeignKeyOrFreeText(option_models['destination'])
    dates = models.CharField(max_length=255, blank=True)
    reason_for_travel = ForeignKeyOrFreeText(option_models['travel_reason'])
    specific_exposures = models.CharField(max_length=255, blank=True)

class Antimicrobial(Subrecord):
    drug = ForeignKeyOrFreeText(option_models['antimicrobial'])
    dose = models.CharField(max_length=255, blank=True)
    route = ForeignKeyOrFreeText(option_models['antimicrobial_route'])
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

class MicrobiologyInput(Subrecord):
    date = models.DateField(null=True, blank=True)
    initials = models.CharField(max_length=255, blank=True)
    clinical_discussion = models.TextField(blank=True)
    agreed_plan = models.TextField(blank=True)
    discussed_with = models.CharField(max_length=255, blank=True)
    clinical_advice_given = models.BooleanField()
    giving_result = models.BooleanField()
    infection_control_advice_given = models.BooleanField()
    change_in_antibiotic_prescription = models.BooleanField()

class Plan(SingletonSubrecord):
    plan = models.TextField(blank=True)

class Discharge(SingletonSubrecord):
    plan = models.TextField(blank=True)

@receiver(models.signals.post_save, sender=Patient)
def create_singletons(sender, **kwargs):
    if kwargs['created']:
        patient = kwargs['instance']
        for subclass in SingletonSubrecord.__subclasses__():
            subclass.objects.create(patient=patient)
