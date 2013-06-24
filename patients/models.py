from collections import OrderedDict

from django.db import models
from django.dispatch import receiver
from django.contrib import auth

from utils.fields import ForeignKeyOrFreeText
from utils import camelcase_to_underscore
from options.models import option_models

TAGS = OrderedDict([
    ('microbiology', 'Micro'),
    ('infectious_diseases', 'ID'),
    ('hiv', 'HIV'),
    ('tropical_diseases', 'Tropical'),
    ('mine', 'Mine'),
])

class PatientManager(models.Manager):
    def get_query_set(self):
        queryset = super(PatientManager, self).get_query_set()
        values = queryset.values('demographics__hospital_number').annotate(id=models.Max('id')).values('id')
        ids = [d['id'] for d in values]
        return queryset.filter(id__in=ids)

class Patient(models.Model):
    # We normally only want the most recent record for each hospital number
    objects = PatientManager()

    def __unicode__(self):
        return '%s | %s' % (self.demographics.hospital_number, self.demographics.name)

    def set_tags(self, tags, user):
        # tags is a dictionary mapping tag names to a boolean
        for tagging in self.tagging_set.all():
            if not tags.get(tagging.tag_name, False):
                tagging.delete()

        for tag_name, value in tags.items():
            if not value:
                continue
            if tag_name not in [t.tag_name for t in self.tagging_set.all()]:
                tagging = Tagging(tag_name=tag_name)
                if tag_name == 'mine':
                    tagging.user = user
                self.tagging_set.add(tagging)

class Tagging(models.Model):
    tag_name = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(auth.models.User, null=True, blank=True)
    patient = models.ForeignKey(Patient)

    def __unicode__(self):
        if self.user is not None:
            return 'User: %s' % self.user.username
        else:
            return self.tag_name

class SingletonSubrecordBase(models.base.ModelBase):
    def __new__(cls, name, bases, attrs):
        if name == 'SingletonSubrecord':
            attrs['Meta'] = type('Meta', (object,), {'abstract': True})
        else:
            related_name = camelcase_to_underscore(name)
            attrs['patient'] = models.OneToOneField(Patient, related_name=related_name)
        return super(SingletonSubrecordBase, cls).__new__(cls, name, bases, attrs)

class SubrecordBase(models.base.ModelBase):
    def __new__(cls, name, bases, attrs):
        if name == 'Subrecord':
            attrs['Meta'] = type('Meta', (object,), {'abstract': True})
        else:
            related_name = camelcase_to_underscore(name)
            attrs['patient'] = models.ForeignKey(Patient, related_name=related_name)
        return super(SubrecordBase, cls).__new__(cls, name, bases, attrs)

class SingletonSubrecord(models.Model):
    __metaclass__ = SingletonSubrecordBase

class Subrecord(models.Model):
    __metaclass__ = SubrecordBase

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
    _title = 'General Notes'
    date = models.DateField(null=True, blank=True)
    comment = models.TextField()

class Travel(Subrecord):
    destination = ForeignKeyOrFreeText(option_models['destination'])
    dates = models.CharField(max_length=255, blank=True)
    reason_for_travel = ForeignKeyOrFreeText(option_models['travel_reason'])
    specific_exposures = models.CharField(max_length=255, blank=True)

class Antimicrobial(Subrecord):
    _title = 'Antimicrobials'
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
    discharge = models.TextField(blank=True)

class MicrobiologyTest(Subrecord):
    test = models.CharField(max_length=255)
    date_ordered = models.DateField(null=True, blank=True)
    details = models.CharField(max_length=255, blank=True)
    microscopy = models.CharField(max_length=255, blank=True)
    organism = models.CharField(max_length=255, blank=True)
    sensitive_antibiotics = models.CharField(max_length=255, blank=True)
    resistant_antibiotics = models.CharField(max_length=255, blank=True)
    result = models.CharField(max_length=20, blank=True)
    igm = models.CharField(max_length=20, blank=True)
    igg = models.CharField(max_length=20, blank=True)
    vca_igm = models.CharField(max_length=20, blank=True)
    vca_igg = models.CharField(max_length=20, blank=True)
    ebna_igg = models.CharField(max_length=20, blank=True)
    hbsag = models.CharField(max_length=20, blank=True)
    anti_hbs = models.CharField(max_length=20, blank=True)
    anti_hbcore_igm = models.CharField(max_length=20, blank=True)
    anti_hbcore_igg = models.CharField(max_length=20, blank=True)
    rpr = models.CharField(max_length=20, blank=True)
    tppa = models.CharField(max_length=20, blank=True)
    viral_load = models.CharField(max_length=20, blank=True)
    parasitaemia = models.CharField(max_length=20, blank=True)
    hsv = models.CharField(max_length=20, blank=True)
    vzv = models.CharField(max_length=20, blank=True)
    syphilis = models.CharField(max_length=20, blank=True)
    c_difficile_antigenl = models.CharField(max_length=20, blank=True)
    c_difficile_toxin = models.CharField(max_length=20, blank=True)
    species = models.CharField(max_length=20, blank=True)
    hsv_1 = models.CharField(max_length=20, blank=True)
    hsv_2 = models.CharField(max_length=20, blank=True)
    enterovirus = models.CharField(max_length=20, blank=True)
    cmv = models.CharField(max_length=20, blank=True)
    ebv = models.CharField(max_length=20, blank=True)
    influenza_a = models.CharField(max_length=20, blank=True)
    influenza_b = models.CharField(max_length=20, blank=True)
    parainfluenza = models.CharField(max_length=20, blank=True)
    metapneumovirus = models.CharField(max_length=20, blank=True)
    rsv = models.CharField(max_length=20, blank=True)
    adenovirus = models.CharField(max_length=20, blank=True)
    norovirus = models.CharField(max_length=20, blank=True)
    rotavirus = models.CharField(max_length=20, blank=True)
    giardia = models.CharField(max_length=20, blank=True)
    entamoeba_histolytica = models.CharField(max_length=20, blank=True)
    cryptosporidium = models.CharField(max_length=20, blank=True)

@receiver(models.signals.post_save, sender=Patient)
def create_singletons(sender, **kwargs):
    if kwargs['created']:
        patient = kwargs['instance']
        for subclass in SingletonSubrecord.__subclasses__():
            subclass.objects.create(patient=patient)
