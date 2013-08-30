from collections import namedtuple
from datetime import datetime
import random

from django.db import models
from django.dispatch import receiver
from django.forms.models import ModelForm
from django.contrib import auth

from patients import exceptions
from utils.fields import ForeignKeyOrFreeText
from utils import camelcase_to_underscore
from options.models import option_models

class APIException(Exception): pass

Tag = namedtuple('Tag', 'name title subtags')

TAGS = [
    Tag('microbiology', 'Micro', [
            Tag('micro_ortho', 'Micro-Ortho', None),
            Tag('micro_icu', 'Micro-ICU', None),
            Tag('micro_haem', 'Micro-Haem', None),
            Tag('micro_nhnn', 'Micro-NHNN', None),
            Tag('micro_heart', 'Micro-Heart', None),
            Tag('micro_tower_review', 'Tower Review', None),
            Tag('micro_handover', 'Micro-Handover', None),
            ]),
    Tag('infectious_diseases', 'ID', [
            Tag('id_inpatients', 'ID Inpatients', None),
            Tag('id_liaison', 'ID Liaison', None)
            ]),
    Tag('hiv', 'Immune', None),
    Tag('tropical_diseases', 'Tropical', None),
    Tag('mine', 'Mine', None),
]

class Patient(models.Model):
    def __unicode__(self):
        demographics = self.demographics_set.get()
        return '%s | %s' % (demographics.hospital_number, demographics.name)

    def to_dict(self):
        d = {'id': self.id}
        for model in Subrecord.__subclasses__():
            subrecords = model.objects.filter(patient_id=self.id)
            d[model.get_api_name()] = [subrecord.to_dict() for subrecord in subrecords]
        return d

    def update_from_dict(self, data, user):
        demographics = self.demographics_set.get()
        demographics.update_from_dict(data['demographics'], user)

        location = self.location_set.get()
        location.update_from_dict(data['location'], user)

        self.save()

    def get_tag_names(self):
        return [t.tag_name for t in self.tagging_set.all()]

    def set_tags(self, tags, user):
        for tagging in self.tagging_set.all():
            if tagging.tag_name not in tags:
                tagging.delete()

        for tag_name in tags:
            if tag_name not in self.get_tag_names():
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


class Subrecord(models.Model):
    patient = models.ForeignKey(Patient)
    consistency_token = models.CharField(max_length=8)

    _is_singleton = False

    class Meta:
        abstract = True

    def __unicode__(self):
        return u'{0}: {1}'.format(self.get_api_name(), self.patient)

    @classmethod
    def get_api_name(cls):
        return camelcase_to_underscore(cls._meta.object_name)

    @classmethod
    def build_field_schema(cls):
        field_schema = []
        for fieldname in cls._get_fieldnames_to_serialize():
            if fieldname in ['id', 'patient_id']:
                continue

            getter = getattr(cls, 'get_field_type_for_' + fieldname, None)
            if getter is None:
                field = cls._get_field_type(fieldname)
                if field in [models.CharField, ForeignKeyOrFreeText]:
                    field_type = 'string'
                else:
                    field_type = camelcase_to_underscore(field.__name__[:-5])
            else:
                field_type = getter()

            field_schema.append({'name': fieldname, 'type': field_type})

        return field_schema

    @classmethod
    def get_field_type_for_consistency_token(cls):
        return 'token'

    @classmethod
    def _get_fieldnames_to_serialize(cls):
        fieldnames = [f.attname for f in cls._meta.fields]

        for name, value in vars(cls).items():
            if isinstance(value, ForeignKeyOrFreeText):
                fieldnames.append(name)
                fieldnames.remove(name + '_ft')
                fieldnames.remove(name + '_fk_id')

        return fieldnames

    @classmethod
    def _get_field_type(cls, name):
        try:
            return type(cls._meta.get_field_by_name(name)[0])
        except models.FieldDoesNotExist:
            pass

        if name == 'patient_id':
            return models.ForeignKey

        try:
            value = vars(cls)[name]
            if isinstance(value, ForeignKeyOrFreeText):
                return ForeignKeyOrFreeText
        except KeyError:
            pass

        raise Exception('Unexpected fieldname: %s' % name)

    def to_dict(self):
        d = {}
        for name in self._get_fieldnames_to_serialize():
            getter = getattr(self, 'get_' + name, None)
            if getter is not None:
                value = getter()
            else:
                value = getattr(self, name)
            d[name] = value

        return d

    def update_from_dict(self, data, user):
        if self.consistency_token:
            try:
                consistency_token = data.pop('consistency_token')
            except KeyError:
                raise exceptions.APIError('Missing field (consistency_token)')

            if consistency_token != self.consistency_token:
                raise exceptions.ConsistencyError

        unknown_fields = set(data.keys()) - set(self._get_fieldnames_to_serialize())
        if unknown_fields:
            raise APIException('Unexpected fieldname(s): %s' % list(unknown_fields))

        for name, value in data.items():
            setter = getattr(self, 'set_' + name, None)
            if setter is not None:
                setter(value, user)
            else:
                # TODO use form here?
                if value and self._get_field_type(name) == models.fields.DateField:
                    try:
                        value = datetime.strptime(value, '%Y-%m-%d').date()
                    except ValueError:
                        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ').date()

                setattr(self, name, value)

        self.set_consistency_token()
        self.save()

    def set_consistency_token(self):
        self.consistency_token = '%08x' % random.randrange(16**8)


class Demographics(Subrecord):
    _is_singleton = True

    name = models.CharField(max_length=255, blank=True)
    hospital_number = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)


class Location(Subrecord):
    _is_singleton = True

    @classmethod
    def _get_fieldnames_to_serialize(cls):
        fieldnames = super(Location, cls)._get_fieldnames_to_serialize()
        fieldnames.append('tags')
        return fieldnames

    @classmethod
    def get_field_type_for_tags(cls):
        return 'list'

    def get_tags(self):
        return {tag_name: True for tag_name in self.patient.get_tag_names()}

    # value is a dictionary mapping tag names to a boolean
    def set_tags(self, value, user):
        tags = [k for k, v in value.items() if v]
        self.patient.set_tags(tags, user)

    category = models.CharField(max_length=255, blank=True)
    hospital = models.CharField(max_length=255, blank=True)
    ward = models.CharField(max_length=255, blank=True)
    bed = models.CharField(max_length=255, blank=True)
    date_of_admission = models.DateField(null=True, blank=True)
    discharge_date = models.DateField(null=True, blank=True) # TODO rename to date_of_discharge?


class Diagnosis(Subrecord):
    condition = ForeignKeyOrFreeText(option_models['condition'])
    provisional = models.BooleanField()
    details = models.CharField(max_length=255, blank=True)
    date_of_diagnosis = models.DateField(blank=True, null=True)


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
    _title = 'Clinical Advice'
    date = models.DateField(null=True, blank=True)
    initials = models.CharField(max_length=255, blank=True)
    reason_for_interaction = ForeignKeyOrFreeText(option_models['clinical_advice_reason_for_interaction'])
    clinical_discussion = models.TextField(blank=True)
    agreed_plan = models.TextField(blank=True)
    discussed_with = models.CharField(max_length=255, blank=True)
    clinical_advice_given = models.BooleanField()
    infection_control_advice_given = models.BooleanField()
    change_in_antibiotic_prescription = models.BooleanField()
    referred_to_opat = models.BooleanField()


class Todo(Subrecord):
    _title = 'To Do'
    details = models.TextField(blank=True)


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
    c_difficile_antigen = models.CharField(max_length=20, blank=True)
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

# TODO
@receiver(models.signals.post_save, sender=Patient)
def create_singletons(sender, **kwargs):
    if kwargs['created']:
        patient = kwargs['instance']
        for subclass in Subrecord.__subclasses__():
            if subclass._is_singleton:
                subclass.objects.create(patient=patient)
