"""
OPAL Models!
"""
import random
from datetime import datetime

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.dispatch import receiver

from opal.utils import stringport, camelcase_to_underscore
from opal.utils.fields import ForeignKeyOrFreeText
from opal import exceptions

options = stringport(settings.OPAL_OPTIONS_MODULE)

class UserProfile(models.Model):
    """
    Profile for our user
    """
    user                  = models.ForeignKey(User, unique=True)
    force_password_change = models.BooleanField(default=True)


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


class TaggedSubrecordMixin(object):
    # _is_singleton = True

    @classmethod
    def _get_fieldnames_to_serialize(cls):
        fieldnames = super(TaggedSubrecordMixin, cls)._get_fieldnames_to_serialize()
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


class Synonym(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = (('name', 'content_type'))

    def __unicode__(self):
        return self.name


option_models = {}

model_names = options.model_names

for name in model_names:
    class_name = name.capitalize() # TODO handle camelcase properly
    bases = (models.Model,)
    attrs = {
        'name': models.CharField(max_length=255, unique=True),
        'synonyms': generic.GenericRelation('Synonym'),
        'Meta': type('Meta', (object,), {'ordering': ['name']}),
        '__unicode__': lambda self: self.name,
        '__module__': __name__,
    }
    option_models[name] = type(class_name, bases, attrs)

# TODO
@receiver(models.signals.post_save, sender=Patient)
def create_singletons(sender, **kwargs):
    if kwargs['created']:
        patient = kwargs['instance']
        for subclass in Subrecord.__subclasses__():
            if subclass._is_singleton:
                subclass.objects.create(patient=patient)
