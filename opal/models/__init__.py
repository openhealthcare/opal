"""
OPAL Models!
"""
import collections
import json

from django.conf import settings
from django.db import models
from django.contrib import auth
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.dispatch import receiver
import reversion

from opal.utils import stringport, camelcase_to_underscore
from opal.utils.fields import ForeignKeyOrFreeText
from opal import exceptions

# Imported models from module.

from opal.models.mixins import TaggedSubrecordMixin, UpdatesFromDictMixin

options = stringport(settings.OPAL_OPTIONS_MODULE)



from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Profile for our user
    """
    user                  = models.ForeignKey(User, unique=True)
    force_password_change = models.BooleanField(default=True)
    can_extract           = models.BooleanField(default=False)
    readonly              = models.BooleanField(default=False)

class Filter(models.Model):
    """
    Saved filters for users extracting data.
    """
    user     = models.ForeignKey(User)
    name     = models.CharField(max_length=200)
    criteria = models.TextField()


class Patient(models.Model):
    def __unicode__(self):
        demographics = self.demographics_set.get()
        return '%s | %s' % (demographics.hospital_number, demographics.name)

    def create_episode(self):
        if self.get_active_episode() is None:
            return self.episode_set.create()
        else:
            raise exceptions.APIError('Patient %s already has active episode' % self)

    def get_active_episode(self):
        for episode in self.episode_set.order_by('id').reverse():
            if episode.is_active():
                return episode
        return None

    def to_dict(self, user):
        active_episode = self.get_active_episode()
        d = {
            'id': self.id,
            'episodes': {episode.id: episode.to_dict(user) for episode in self.episode_set.all()},
            'active_episode_id': active_episode.id if active_episode else None,
            }

        for model in PatientSubrecord.__subclasses__():
            subrecords = model.objects.filter(patient_id=self.id)
            d[model.get_api_name()] = [subrecord.to_dict(user) for subrecord in subrecords]
        return d

    def update_from_demographics_dict(self, demographics_data, user):
        demographics = self.demographics_set.get()
        demographics.update_from_dict(demographics_data, user)


class Episode(UpdatesFromDictMixin, models.Model):
    """
    An individual episode of care.

    A patient may have many episodes of care, but this maps to one occasion
    on which they found themselves on "The List".
    """
    patient = models.ForeignKey(Patient)
    active  = models.BooleanField(default=False)
    date_of_admission = models.DateField(null=True, blank=True)
    # TODO rename to date_of_discharge?
    discharge_date = models.DateField(null=True, blank=True)
    consistency_token = models.CharField(max_length=8)

    def __unicode__(self):
        demographics = self.patient.demographics_set.get()

        return '%s | %s | %s' % (demographics.hospital_number,
                                 demographics.name,
                                 self.date_of_admission)

    def is_active(self):
        # TODO Depreciate this.
        #
        # This is only here for API compatability.
        # Don't use me!
        return self.active

    def set_tag_names(self, tag_names, user):
        """
        1. Blitz dangling tags not in our current dict.
        2. Add new tags.
        3. Make sure that we set the Active boolean appropriately
        4. There is no step 4.
        """
        original_tag_names = self.get_tag_names(user)

        for tag_name in original_tag_names:
            if tag_name not in tag_names:
                params = {'tag_name': tag_name}
                if tag_name == 'mine':
                    params['user'] = user
                self.tagging_set.get(**params).delete()

        for tag_name in tag_names:
            if tag_name not in original_tag_names:
                params = {'tag_name': tag_name}
                if tag_name == 'mine':
                    params['user'] = user
                self.tagging_set.create(**params)

        if len(tag_names) < 1:
            self.active = False
        elif tag_names == ['mine']:
            self.active = False
        elif not self.active:
            self.active = True
        self.save()

    def get_tag_names(self, user):
        return [t.tag_name for t in self.tagging_set.all() if t.user in (None, user)]

    def to_dict(self, user, shallow=False):
        """
        Serialisation to JSON for Episodes
        """
        d = {
            'id'               : self.id,
            'active'           : self.active,
            'date_of_admission': self.date_of_admission,
            'discharge_date'   : self.discharge_date,
            'consistency_token': self.consistency_token
            }
        if shallow:
            return d

        for model in PatientSubrecord.__subclasses__():
            subrecords = model.objects.filter(patient_id=self.patient.id)
            d[model.get_api_name()] = [subrecord.to_dict(user)
                                       for subrecord in subrecords]
        for model in EpisodeSubrecord.__subclasses__():
            subrecords = model.objects.filter(episode_id=self.id)
            d[model.get_api_name()] = [subrecord.to_dict(user)
                                       for subrecord in subrecords]
        d['prev_episodes'] = []
        d['next_episodes'] = []

        if self.date_of_admission:
            eset = self.patient.episode_set

            d['prev_episodes'] = [
                e.to_dict(user, shallow=True)
                for e in
                eset.filter(date_of_admission__lt=self.date_of_admission).order_by('date_of_admission')]
            d['next_episodes'] = [
                e.to_dict(user, shallow=True)
                for e in
                eset.filter(date_of_admission__gt=self.date_of_admission).order_by('date_of_admission')]

        return d

    def update_from_location_dict(self, location_data, user):
        # TODO Completely depreciate this.
        location = self.location_set.get()
        location.update_from_dict(location_data, user)


class Tagging(models.Model):
    tag_name = models.CharField(max_length=255)
    user = models.ForeignKey(auth.models.User, null=True)
    episode = models.ForeignKey(Episode, null=True) # TODO make null=False

    def __unicode__(self):
        if self.user is not None:
            return 'User: %s - %s' % (self.user.username, self.tag_name)
        else:
            return self.tag_name

    @classmethod
    def historic_tags_for_episodes(cls, episodes):
        """
        Given a list of episodes, return a dict indexed by episode id
        that contains historic tags for those episodes.
        """
        deleted = reversion.get_deleted(cls)
        historic = collections.defaultdict(dict)
        for d in deleted:
            data = json.loads(d.serialized_data)[0]['fields']
            if data['episode'] in episodes:
                historic[data['episode']][data['tag_name']] = True
        return historic


class Subrecord(UpdatesFromDictMixin, models.Model):
    consistency_token = models.CharField(max_length=8)

    _is_singleton = False

    class Meta:
        abstract = True

    def __unicode__(self):
        return u'{0}: {1}'.format(self.get_api_name(), self.id)

    @classmethod
    def get_api_name(cls):
        return camelcase_to_underscore(cls._meta.object_name)

    @classmethod
    def build_field_schema(cls):
        field_schema = []
        for fieldname in cls._get_fieldnames_to_serialize():
            if fieldname in ['id', 'patient_id', 'episode_id']:
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

    def to_dict(self, user):
        d = {}
        for name in self._get_fieldnames_to_serialize():
            getter = getattr(self, 'get_' + name, None)
            if getter is not None:
                value = getter(user)
            else:
                value = getattr(self, name)
            d[name] = value

        return d


class PatientSubrecord(Subrecord):
    patient = models.ForeignKey(Patient)

    class Meta:
        abstract = True


class EpisodeSubrecord(Subrecord):
    episode = models.ForeignKey(Episode, null=True)  # TODO make null=False

    class Meta:
        abstract = True


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
def create_patient_singletons(sender, **kwargs):
    if kwargs['created']:
        patient = kwargs['instance']
        for subclass in PatientSubrecord.__subclasses__():
            if subclass._is_singleton:
                subclass.objects.create(patient=patient)


@receiver(models.signals.post_save, sender=Episode)
def create_episode_singletons(sender, **kwargs):
    if kwargs['created']:
        episode = kwargs['instance']
        for subclass in EpisodeSubrecord.__subclasses__():
            if subclass._is_singleton:
                subclass.objects.create(episode=episode)
