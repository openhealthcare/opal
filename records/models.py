import random

from django.core.exceptions import FieldError
from django.db import models
from django.forms.models import ModelForm
from rest_framework.utils.encoders import JSONEncoder

from records import exceptions

class Patient(models.Model):
    def serialize(self):
        data = {'id': self.id}
        data['admissions'] = [admission.serialize() for admission in self.admission_set.all()]
        for model in PatientSubrecord.__subclasses__():
            name = model.__name__.lower()
            subrecord_set = getattr(self, name + '_set').all() 
            data[name] = [subrecord.serialize() for subrecord in subrecord_set]
        return data


class Admission(models.Model):
    patient = models.ForeignKey(Patient)

    def serialize(self):
        data = {'id': self.id}
        for model in AdmissionSubrecord.__subclasses__():
            name = model.__name__.lower()
            subrecord_set = getattr(self, name + '_set').all() 
            data[name] = [subrecord.serialize() for subrecord in subrecord_set]
        return data

class Subrecord(models.Model):
    class Meta:
        abstract = True

    consistency_token = models.CharField(max_length=8)

    def get_fieldnames_to_serialize(self):
        return [f.attname for f in self._meta.fields]

    def serialize(self):
        fieldnames = sorted(self.get_fieldnames_to_serialize())
        serialization = {name: getattr(self, name) for name in fieldnames}
        return serialization

    def save(self, *args, **kwargs):
        self.set_consistency_token()
        return super(Subrecord, self).save(*args, **kwargs)

    def set_consistency_token(self):
        self.consistency_token = '%08x' % random.randrange(16**8)

    def update(self, data):
        try:
            consistency_token = data.pop('consistency_token')
        except KeyError:
            raise exceptions.APIError('Missing field (consistency_token)')

        if consistency_token != self.consistency_token:
            raise exceptions.ConsistencyError('')

        try:
            model_form_class = self._build_model_form_class(data)
        except FieldError as e:
            raise exceptions.APIError(*e.args)

        model_form = model_form_class(instance=self, data=data)

        try:
            model_form.save()
        except ValueError:
            raise exceptions.APIError('Invalid value for field(s) (%s)' % ''.join(model_form.errors.keys()))

    @classmethod
    def _build_model_form_class(cls, data):
        class Meta:
            model = cls
            fields = data.keys()
        return type(cls.__name__ + 'ModelForm', (ModelForm,), {'Meta': Meta})


class PatientSubrecord(Subrecord):
    class Meta:
        abstract = True

    patient = models.ForeignKey(Patient)


class AdmissionSubrecord(Subrecord):
    class Meta:
        abstract = True

    admission = models.ForeignKey(Admission)

    @property
    def patient(self):
        return self.admission.patient

    @property
    def patient_id(self):
        return self.patient.id

def get_subrecord_model(name):
    for model in PatientSubrecord.__subclasses__():
        if model.__name__.lower() == name:
            return model
    for model in AdmissionSubrecord.__subclasses__():
        if model.__name__.lower() == name:
            return model
    return None
