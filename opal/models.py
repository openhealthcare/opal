"""
Opal Django Models
"""
import datetime
import functools
import hashlib
import itertools
import json
import logging
import random
import os

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import FieldDoesNotExist
from django.db import models, transaction
from django.db.models import Q
from django.db.models.signals import post_save
from django.template.loader import get_template
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils import timezone

from opal.core import (
    application, exceptions, lookuplists, plugins, patient_lists, tagging
)
from opal import managers
from opal.utils import camelcase_to_underscore, find_template
from opal.core import serialization
from opal.core.fields import ForeignKeyOrFreeText, enum
from opal.core.referencedata import models as referencemodels
from opal.core.subrecords import (
    episode_subrecords, patient_subrecords, get_subrecord_from_api_name
)


def get_default_episode_type():
    app = application.get_app()
    return app.default_episode_category


class SerialisableFields(object):
    """
    Mixin class that handles the getting of fields
    and field types for serialisation/deserialization
    """
    @classmethod
    def _get_fieldnames_to_serialize(cls):
        """
        Return the list of field names we want to serialize.
        """
        # TODO update to use the django 1.8 meta api
        fieldnames = [f.attname for f in cls._meta.fields]
        for name, value in list(vars(cls).items()):
            if isinstance(value, ForeignKeyOrFreeText):
                fieldnames.append(name)
        # Sometimes FKorFT fields are defined on the parent now we have
        # core archetypes - find those fields.
        ftfk_fields = [f for f in fieldnames if f.endswith('_fk_id')]
        for f in ftfk_fields:
            if f[:-6] in fieldnames:
                continue
            fieldnames.append(f[:-6])

        fields = cls._meta.get_fields(include_parents=True)

        def m2m(x):
            """
            Predicate function to determine whether something
            is a ManyToMany field
            """
            return isinstance(x, (
                models.fields.related.ManyToManyField,
                models.fields.related.ManyToManyRel
            ))

        many_to_manys = [field.name for field in fields if m2m(field)]

        fieldnames = fieldnames + many_to_manys
        fieldnames = [
            f for f in fieldnames
            if not any((f.endswith('_fk_id'), f.endswith('_ft')))
        ]
        return fieldnames

    @classmethod
    def _get_field_type(cls, name):
        try:
            return type(cls._meta.get_field(name))
        except models.FieldDoesNotExist:
            pass

        # TODO: Make this dynamic
        if name in ['patient_id', 'episode_id']:
            return models.ForeignKey

        try:
            value = getattr(cls, name)
            if isinstance(value, ForeignKeyOrFreeText):
                return ForeignKeyOrFreeText

        except AttributeError:
            pass

        raise exceptions.UnexpectedFieldNameError(
            'Unexpected fieldname: %s' % name
        )

    @classmethod
    def get_human_readable_type(cls, field_name):
        field_type = cls._get_field(field_name)

        if isinstance(field_type, models.BooleanField):
            return "Either True or False"
        if isinstance(field_type, models.NullBooleanField):
            return "Either True, False or None"
        if isinstance(field_type, models.DateTimeField):
            return "Date & Time"
        if isinstance(field_type, models.DateField):
            return "Date"

        numeric_fields = (
            models.AutoField,
            models.BigIntegerField,
            models.IntegerField,
            models.FloatField,
            models.DecimalField,
        )
        if isinstance(field_type, numeric_fields):
            return "Number"

        if isinstance(field_type, ForeignKeyOrFreeText):
            t = "Normally coded as a {} but free text entries are possible."
            return t.format(field_type.foreign_model._meta.object_name.lower())

        related_fields = (
            models.ForeignKey, models.ManyToManyField,
        )
        if isinstance(field_type, related_fields):
            if isinstance(field_type, models.ForeignKey):
                t = "One of the {}"
            else:
                t = "Some of the {}"
            related = field_type.remote_field.model
            return t.format(related._meta.verbose_name_plural.title())

        enum = cls.get_field_enum(field_name)

        if enum:
            return "One of {}".format(",".join([force_str(e) for e in enum]))

        else:
            return "Text Field"

    @classmethod
    def _get_field(cls, name):
        try:
            return cls._meta.get_field(name)
        except FieldDoesNotExist:
            return getattr(cls, name)

    @classmethod
    def _get_field_title(cls, name):
        field = cls._get_field(name)
        if isinstance(field, models.ManyToOneRel):
            field_name = field.related_model._meta.verbose_name_plural
        else:
            field_name = field.verbose_name

        if field_name.islower():
            field_name = field_name.title()

        return field_name

    @classmethod
    def _get_field_default(cls, name):
        field = cls._get_field(name)

        if isinstance(field, models.ManyToOneRel):
            default = []
        else:
            default = field.get_default()

        # for blank fields the result is a blank string, lets just remove that
        if default == '':
            return None

        if isinstance(default, datetime.date):
            raise exceptions.APIError(
                "{0}.{1} returned a date as a default, Opal currently does "
                "not support sending dates/datetimes as defaults".format(
                    cls, name
                )
            )

        return default

    @classmethod
    def get_field_description(cls, name):
        field = cls._get_field(name)
        description = getattr(field, 'help_text', "")
        if description:
            return description

    @classmethod
    def get_field_enum(cls, name):
        field = cls._get_field(name)
        choices = getattr(field, "choices", [])

        if choices:
            return [i[1] for i in choices]

    @classmethod
    def get_lookup_list_api_name(cls, field_name):
        lookup_list = None
        field_type = cls._get_field_type(field_name)
        if field_type == ForeignKeyOrFreeText:
            fld = getattr(cls, field_name)
            lookup_list = camelcase_to_underscore(
                fld.foreign_model.get_api_name()
            )
        elif field_type == models.fields.related.ManyToManyField:
            related_model = getattr(cls, field_name).field.related_model
            if issubclass(related_model, lookuplists.LookupList):
                return related_model.get_api_name()
        return lookup_list

    @classmethod
    def build_schema_for_field_name(cls, field_name):
        getter = getattr(cls, 'get_field_type_for_' + field_name, None)
        if getter is None:
            field = cls._get_field_type(field_name)
            if field in [models.CharField, ForeignKeyOrFreeText]:
                field_type = 'string'
            else:
                field_type = camelcase_to_underscore(field.__name__[:-5])
        else:
            field_type = getter()

        title = cls._get_field_title(field_name)
        default = cls._get_field_default(field_name)
        field = {
            'name': field_name,
            'title': title,
            'type': field_type,
            'lookup_list': cls.get_lookup_list_api_name(field_name),
            'default': default,
            'model': cls.__name__,
            'description': cls.get_field_description(field_name),
            'enum': cls.get_field_enum(field_name)
        }
        return field

    @classmethod
    def build_field_schema(cls):
        field_schema = []

        for fieldname in cls._get_fieldnames_to_serialize():
            if fieldname in ['id', 'patient_id', 'episode_id']:
                continue
            field_schema.append(cls.build_schema_for_field_name(fieldname))
        return field_schema


class UpdatesFromDictMixin(SerialisableFields):
    """
    Mixin class to provide the deserialization
    fields, as well as update logic for our JSON APIs.
    """

    @classmethod
    def _get_fieldnames_to_extract(cls):
        """
        Return a list of fieldname to extract - which means dumping
        PID fields.
        """
        fieldnames = cls._get_fieldnames_to_serialize()
        if hasattr(cls, 'pid_fields'):
            for fname in cls.pid_fields:
                if fname in fieldnames:
                    fieldnames.remove(fname)
        return fieldnames

    @classmethod
    def get_field_type_for_consistency_token(cls):
        return 'token'

    def set_consistency_token(self):
        self.consistency_token = '%08x' % random.randrange(16**8)

    def get_lookup_list_values_for_names(self, lookuplist, names):
        ct = ContentType.objects.get_for_model(lookuplist)

        return lookuplist.objects.filter(
            models.Q(name__in=names) | models.Q(
                synonyms__name__in=names, synonyms__content_type=ct
            )
        )

    def save_many_to_many(self, name, values, field_type):
        field = getattr(self, name)
        new_lookup_values = self.get_lookup_list_values_for_names(
            field.model, values
        )

        new_values = new_lookup_values.values_list("id", flat=True)
        existing_values = field.all().values_list("id", flat=True)

        to_add = set(new_values) - set(existing_values)
        to_remove = set(existing_values) - set(new_values)

        if len(set(new_values)) != len(set(values)):
            # the only way this should happen is if one of the incoming
            # values is a synonym for another incoming value so lets check this
            synonym_found = False
            new_names = new_lookup_values.filter(name__in=values)
            values_set = set(values)

            for new_name in new_names:
                synonyms = set(new_name.synonyms.all().values_list(
                    "name", flat=True)
                )
                if values_set.intersection(synonyms):
                    synonym_found = True
                    logging.info("found synonym {0} for {1}".format(
                        synonyms, values_set)
                    )
                    break

            if not synonym_found:
                error_msg = 'Unexpected fieldname(s): {}'.format(values)
                raise exceptions.APIError(error_msg)

        field.add(*to_add)
        field.remove(*to_remove)

    def update_from_dict(self, data, user, force=False, fields=None):
        logging.info("updating {0} with {1} for {2}".format(
            self.__class__.__name__, data, user
        ))
        if fields is None:
            fields = set(self._get_fieldnames_to_serialize())

        if self.consistency_token and not force:
            try:
                consistency_token = data.pop('consistency_token')
            except KeyError:
                msg = 'Missing field (consistency_token) for {}'
                raise exceptions.MissingConsistencyTokenError(
                    msg.format(self.__class__.__name__)
                )

            if consistency_token != self.consistency_token:
                raise exceptions.ConsistencyError

        post_save = []

        unknown_fields = set(data.keys()) - fields

        if unknown_fields:
            raise exceptions.APIError(
                'Unexpected fieldname(s): %s' % list(unknown_fields))

        for name in fields:
            value = data.get(name, None)

            if name == 'consistency_token':
                continue  # shouldn't be needed - Javascripts bug?
            setter = getattr(self, 'set_' + name, None)
            if setter is not None:
                setter(value, user, data)
            else:
                if name in data:
                    field_type = self._get_field_type(name)

                    if field_type == models.fields.related.ManyToManyField:
                        post_save.append(
                            functools.partial(self.save_many_to_many,
                                              name,
                                              value,
                                              field_type))
                    else:
                        DateTimeField = models.fields.DateTimeField
                        if value and field_type == models.fields.DateField:
                            value = serialization.deserialize_date(value)
                        elif value and field_type == DateTimeField:
                            value = serialization.deserialize_datetime(value)
                        elif value and field_type == models.fields.TimeField:
                            value = serialization.deserialize_time(value)

                        setattr(self, name, value)

        self.set_consistency_token()
        self.save()

        for some_func in post_save:
            some_func()


class ToDictMixin(SerialisableFields):
    """
    Mixin that adds methods to serialise a subrecord to a dictionary
    """
    def to_dict(self, user, fields=None):
        """
        Allow a subset of FIELDNAMES
        """

        if fields is None:
            fields = self._get_fieldnames_to_serialize()

        d = {}
        for name in fields:
            getter = getattr(self, 'get_' + name, None)
            if getter is not None:
                value = getter(user)
            else:
                field_type = self._get_field_type(name)
                if field_type == models.fields.related.ManyToManyField:
                    qs = getattr(self, name).all()
                    value = [i.to_dict(user) for i in qs]
                else:
                    value = getattr(self, name)
            d[name] = value

        return d


class Synonym(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = (('name', 'content_type'))

    def __str__(self):
        return self.name


class Patient(models.Model):
    """
    An individual receiving health care

    This model maps, generaly speaking, to the FHIR profile Patient.

    - We allow one name per patient, and add the fields from a FHIR HumanName directly
    - We do not implement the multipleBirth fields
    - One Address per patient as a text field (complex address models can be easily added in application scope)
    - We omit photo (Can be added in application scope as a subrecord)
    - We add the fields birth_place and ethnicity as these have been frequently required
    - We omit references to a communication, GP, managing organization and link (these can be added in application scope)
    """
    objects = managers.PatientQueryset.as_manager()

    SEX_CHOICES = enum('Male', 'Female', 'Other', 'Unknown')


    # .identifier is implicit (a PatientSubrecord)
    active            = models.BooleanField(default=True, help_text="Whether this patient record is in active use")

    # .name fields loaded directly and accessible as a text string via the .name property
    name_prefex       = models.CharField(max_length=255, blank=True, null=True, help_text="Parts that come before the name")
    family_name       = models.CharField(max_length=255, blank=True, null=True, help_text="Often called 'Surname'")
    given_names       = models.CharField(max_length=255, blank=True, null=True, help_text="Often called first. Also includes middle")
    name_suffix       = models.CharField(max_length=255, blank=True, null=True, help_text="Parts that come after the name")

    # .telecom is implicit (ContactPoint is a subrecord)

    # This is equivalent to .gender in the FHIR Patient profile
    sex               = models.CharField(max_length=50, choices=SEX_CHOICES, blank=True, null=True)

    birth_date        = models.DateField(null=True, blank=True, verbose_name="Date of Birth")
    deceased          = models.BooleanField(default=False, help_text="This field will be True if the patient is deceased.")
    deceased_datetime = models.DateTimeField(null=True, blank=True, verbose_name="Date and time of death")

    address_text      = models.TextField(blank=True, null=True, help_text="Text representation of the address")
    marital_status    = ForeignKeyOrFreeText(referencemodels.MaritalStatus)

    birth_place = ForeignKeyOrFreeText(referencemodels.Country, verbose_name="Country of Birth")
    ethnicity = ForeignKeyOrFreeText(referencemodels.Ethnicity)


    def __str__(self):
        return 'Patient {0}'.format(self.id)

    @property
    def name(self):
        return f"{self.name_prefix} {self.given_names} {self.family_name} {self.name_suffix}".strip()

    def get_absolute_url(self):
        """
        Return the URL for this patient
        """
        return reverse('patient_detail', args=[self.pk])

    def create_episode(self, **kwargs):
        return self.episode_set.create(**kwargs)

    def get_active_episode(self):
        for episode in self.episode_set.order_by('id').reverse():
            if episode.active:
                return episode
        return None

    @transaction.atomic()
    def bulk_update(self, dict_of_list_of_upgrades, user,
                    episode=None, force=False):
        """
                takes in a dictionary of api name to a list of fields and
                creates the required subrecords. If passed an episode
                sub record but no episode it will create an episode
                and attatch it.

                e.g. {"allergies": [
                            {"drug": "paracetomol"}
                            {"drug": "aspirin"}
                          ],
                      "diagnosis":[
                            {
                                "condition": "some test",
                                "details": "some details"
                            }
                          ]
                     }
        """
        if "demographics" not in dict_of_list_of_upgrades:
            if not self.id:
                dict_of_list_of_upgrades["demographics"] = [{}]

        if not self.id:
            self.save()

        #
        # We never want to be in the position where we don't have an episode.
        # If this patient has never had an episode, we create one now.
        # If the patient has preexisting episodes, we will either use an
        # episode passed in to us as a kwarg, or create a fresh episode for
        # this bulk update once we're sure we have episode subrecord data to
        # save.
        #
        if not self.episode_set.exists():
            episode = self.create_episode()

        for api_name, list_of_upgrades in dict_of_list_of_upgrades.items():

            if(api_name == "tagging"):
                episode.set_tag_names_from_tagging_dict(
                    list_of_upgrades[0], user
                )
                continue

            model = get_subrecord_from_api_name(api_name=api_name)
            if model in episode_subrecords():
                if episode is None:
                    episode = self.create_episode()
                    episode.save()

                model.bulk_update_from_dicts(episode, list_of_upgrades, user,
                                             force=force)
            else:
                # it's a patient subrecord
                model.bulk_update_from_dicts(self, list_of_upgrades, user,
                                             force=force)

    def to_dict(self, user):
        d = {
            'id': self.id,
            'episodes': {episode.id: episode.to_dict(user) for episode in
                         self.episode_set.all()}
        }

        for model in patient_subrecords():
            subrecords = model.objects.filter(patient_id=self.id)
            d[model.get_api_name()] = [
                subrecord.to_dict(user) for subrecord in subrecords
            ]
        return d

    def update_from_demographics_dict(self, demographics_data, user):
        self.demographics().update_from_dict(demographics_data, user)

    def save(self, *args, **kwargs):
        created = not bool(self.id)
        super(Patient, self).save(*args, **kwargs)
        if created:
            for subclass in patient_subrecords():
                if subclass._is_singleton:
                    subclass.objects.create(patient=self)



class ExternallySourcedModel(models.Model):
    # the system upstream that contains this model
    external_system = models.CharField(
        blank=True, null=True, max_length=255
    )

    # the identifier used by the upstream system
    external_identifier = models.CharField(
        blank=True, null=True, max_length=255
    )

    class Meta:
        abstract = True

    @classmethod
    def get_modal_footer_template(cls):
        return "partials/_sourced_modal_footer.html"


class TrackedModel(models.Model):
    # these fields are set automatically from REST requests via
    # updates from dict and the getter, setter properties, where available
    # (from the update from dict mixin)
    created = models.DateTimeField(blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True,
        related_name="created_%(app_label)s_%(class)s_subrecords",
        on_delete=models.SET_NULL
    )
    updated_by = models.ForeignKey(
        User, blank=True, null=True,
        related_name="updated_%(app_label)s_%(class)s_subrecords",
        on_delete=models.SET_NULL
    )

    class Meta:
        abstract = True

    def set_created_by_id(self, incoming_value, user, *args, **kwargs):
        if not self.id:
            # this means if a record is not created by the api, it will not
            # have a created by id
            self.created_by = user

    def set_updated_by_id(self, incoming_value, user, *args, **kwargs):
        if self.id:
            self.updated_by = user

    def set_updated(self, incoming_value, user, *args, **kwargs):
        if self.id:
            self.updated = timezone.now()

    def set_created(self, incoming_value, user, *args, **kwargs):
        if not self.id:
            # this means if a record is not created by the api, it will not
            # have a created timestamp

            self.created = timezone.now()


class Episode(UpdatesFromDictMixin, TrackedModel):
    """
    An individual episode of care.

    A patient may have many episodes of care, but this maps to one occasion
    on which they found themselves on "The List".
    """
    category_name     = models.CharField(
        max_length=200, default=get_default_episode_type
    )
    patient           = models.ForeignKey(Patient, on_delete=models.CASCADE)
    active            = models.BooleanField(default=False)
    start             = models.DateField(null=True, blank=True)
    end               = models.DateField(blank=True, null=True)
    consistency_token = models.CharField(max_length=8)

    # stage is at what stage of an episode flow is the
    # patient at
    stage             = models.CharField(
        max_length=256, null=True, blank=True
    )

    objects = managers.EpisodeQueryset.as_manager()

    def __init__(self, *args, **kwargs):
        super(Episode, self).__init__(*args, **kwargs)
        self.__original_active = self.active

    def __str__(self):
        return 'Episode {0}: {1} - {2}'.format(
            self.pk, self.start, self.end
        )

    def get_absolute_url(self):
        """
        Return the URL for this Episode
        """
        return '/#/patient/{}/{}'.format(self.patient_id, self.id)

    def save(self, *args, **kwargs):
        created = not bool(self.id)

        current_active_value = self.active
        category_active_value = self.category.is_active()

        if current_active_value != category_active_value:  # Disagreement
            if current_active_value != self.__original_active:
                # The value of self.active has been set by some code somewhere
                # not by __init__() e.g. the original database value at the
                # time of instance initalization.
                #
                # Rather than overriding this silently we should raise a
                # ValueError.
                msg = "Value of Episode.active has been set to {} but " \
                      "category.is_active() returns {}"
                raise ValueError(
                    msg.format(current_active_value, category_active_value)
                )

        self.active = category_active_value
        super(Episode, self).save(*args, **kwargs)

        # Re-set this in case we changed it once post initialization and then
        # the user subsequently saves this instance again
        self.__original_active = self.active

        if created:
            for subclass in episode_subrecords():
                if subclass._is_singleton:
                    subclass.objects.create(episode=self)

    @property
    def category(self):
        from opal.core import episodes
        categories = episodes.EpisodeCategory.filter(
            display_name=self.category_name
        )
        if len(categories) == 0:
            msg = "Unable to find EpisodeCategory for category name {0}"
            msg = msg.format(self.category_name)
            raise exceptions.UnexpectedEpisodeCategoryNameError(msg)
        else:
            category = categories[0]
            return category(self)

    def visible_to(self, user):
        """
        Predicate function to determine whether this episode is visible to
        a certain user.

        The logic for visibility is held in individual
        opal.core.episodes.EpisodeCategory implementations.
        """
        return self.category.episode_visible_to(self, user)

    def set_stage(self, stage, user, data):
        """
        Setter for Episode.stage

        Validates that the stage being set is appropriate for the category
        and raises ValueError if not.
        """
        self.category.set_stage(stage, user, data)

    def set_tag_names(self, tag_names, user):
        """
        1. Special case mine
        2. Archive dangling tags not in our current list.
        3. Add new tags.
        4. Ensure that we're setting the parents of child tags
        5. There is no step 6.
        """
        if "mine" not in tag_names:
            self.tagging_set.filter(user=user,
                                    value='mine').update(archived=True)
        else:
            tag, created = self.tagging_set.get_or_create(
                value='mine', user=user
            )
            if not created:
                tag.archived = False
                tag.save()

            tag_names = [t for t in tag_names if not t == 'mine']

        # nuke everything and start from fresh so we don't have
        # to deal with childless parents
        self.tagging_set.exclude(value="mine").filter(archived=False).update(
            archived=True,
            updated_by=user,
            updated=timezone.now()
        )
        parents = []
        for tag in tag_names:
            parent = tagging.parent(tag)
            if parent:
                parents.append(parent)
        tag_names += parents

        for tag in tag_names:
            tagg, created = self.tagging_set.get_or_create(
                value=tag, episode=self
            )
            if created:
                tagg.created_by = user
                tagg.created = timezone.now()
            else:
                tagg.archived = False
                tagg.updated_by = user
                tagg.updated = timezone.now()

            tagg.save()

    def set_tag_names_from_tagging_dict(self, tagging_dict, user):
        """
        Given a dictionary of {tag_name: True} pairs, set tag names
        according to those tags which are truthy.
        """
        tag_names = [n for n, v in list(tagging_dict.items()) if v is True]
        return self.set_tag_names(tag_names, user)

    def tagging_dict(self, user):
        tag_names = self.get_tag_names(user)
        tagging_dict = {i: True for i in tag_names}
        tagging_dict["id"] = self.id
        return [tagging_dict]

    def get_tag_names(self, user, historic=False):
        """
        Return the current active tag names for this Episode as strings.
        """
        qs = self.tagging_set.filter(Q(user=user) | Q(user=None))
        if not historic:
            qs = qs.filter(archived=False)

        return list(qs.values_list("value", flat=True))

    def to_dict(self, user, shallow=False):
        """
        Serialisation to JSON for Episodes
        """
        d = {
            'id'               : self.id,
            'category_name'    : self.category_name,
            'active'           : self.active,
            'consistency_token': self.consistency_token,
            'start'            : self.start,
            'end'              : self.end,
            'stage'            : self.stage,
        }

        if shallow:
            return d

        for model in patient_subrecords():
            subrecords = model.objects.filter(patient_id=self.patient.id)

            d[model.get_api_name()] = [
                subrecord.to_dict(user) for subrecord in subrecords
            ]

        for model in episode_subrecords():
            subrecords = model.objects.filter(episode_id=self.id)

            d[model.get_api_name()] = [
                subrecord.to_dict(user) for subrecord in subrecords
            ]

        d['tagging'] = self.tagging_dict(user)
        return d


class Subrecord(UpdatesFromDictMixin, ToDictMixin, TrackedModel, models.Model):
    _is_singleton            = False
    _advanced_searchable     = True
    _exclude_from_subrecords = False

    consistency_token = models.CharField(max_length=8)

    class Meta:
        abstract = True


    def __str__(self):
        template = get_template(self.get_display_template())
        return template.render({'record': self})

    @classmethod
    def get_class_name(cls):
        return cls.__name__

    @classmethod
    def get_api_name(cls):
        return camelcase_to_underscore(cls._meta.object_name)

    @classmethod
    def get_icon(cls):
        return getattr(cls, '_icon', None)

    @classmethod
    def get_display_name(cls):
        if cls._meta.verbose_name.islower():
            return cls._meta.verbose_name.title()
        return cls._meta.verbose_name

    @classmethod
    def _get_template(cls, template, prefixes=None):
        template_locations = []

        if prefixes is None:
            prefixes = []

        for prefix in prefixes:
            template_locations.append(
                template.format(os.path.join(prefix, cls.get_api_name()))
            )

        template_locations.append(template.format(cls.get_api_name()))
        return find_template(template_locations)

    @classmethod
    def get_display_template(cls, prefixes=None):
        """
        Return the active display template for our record
        """
        if prefixes is None:
            prefixes = []

        return cls._get_template(
            os.path.join("records", "{}.html"),
            prefixes=prefixes
        )

    @classmethod
    def get_detail_template(cls, prefixes=None):
        """
        Return the active detail template for our record
        """
        file_locations = [
            os.path.join('records', '{0}_detail.html'),
            os.path.join('records', '{0}.html'),
        ]

        if prefixes is None:
            prefixes = []

        templates = []

        for prefix in prefixes:
            for file_location in file_locations:
                templates.append(file_location.format(
                    os.path.join(prefix, cls.get_api_name())
                ))

        for file_location in file_locations:
            templates.append(
                file_location.format(cls.get_api_name())
            )
        return find_template(templates)

    @classmethod
    def get_form_template(cls, prefixes=None):
        if prefixes is None:
            prefixes = []

        return cls._get_template(
            template=os.path.join("forms", "{}_form.html"),
            prefixes=prefixes
        )

    @classmethod
    def get_form_url(cls):
        return reverse("form_view", kwargs=dict(model=cls.get_api_name()))

    @classmethod
    def get_modal_template(cls, prefixes=None):
        """
        Return the active form template for our record
        """
        if prefixes is None:
            prefixes = []

        result = cls._get_template(
            template=os.path.join("modals", "{}_modal.html"),
            prefixes=prefixes
        )

        if not result and cls.get_form_template():
            result = find_template(["base_templates/form_modal_base.html"])

        return result

    @classmethod
    def bulk_update_from_dicts(
        cls, parent, list_of_dicts, user, force=False
    ):
        """
            allows the bulk updating of a field for example
            [
                {"test": "blah 1", "details": "blah blah"}
                {"test": "blah 2", "details": "blah blah"}
            ]

            parent is the parent class, that can be Episode or Patient

            this method will not delete. It updates if there's an id or if
            the model is a singleton otherwise it creates
        """
        schema_name = parent.__class__.__name__.lower()

        if cls._is_singleton:
            if len(list_of_dicts) > 1:
                msg = "Attempted creation of multiple fields on a singleton {}"
                raise ValueError(msg.format(cls.__name__))

        result = []

        for a_dict in list_of_dicts:
            if "id" in a_dict or cls._is_singleton:
                if cls._is_singleton:
                    query = cls.objects.filter(**{schema_name: parent})
                    subrecord = query.get()
                else:
                    subrecord = cls.objects.get(id=a_dict["id"])
            else:
                a_dict["{}_id".format(schema_name)] = parent.id
                subrecord = cls(**{schema_name: parent})

            subrecord.update_from_dict(a_dict, user, force=force)
            result.append(subrecord)
        return result

    def get_edit_url(self):
        return reverse('edit-subrecord', args=[self.get_class_name(), self.pk])



class PatientSubrecord(Subrecord):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class EpisodeSubrecord(Subrecord):

    episode = models.ForeignKey(Episode, null=False, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Identifier(PatientSubrecord):
    """
    A unique identifier for a Patient e.g. their Hospital Number or NHS Number

    While this model maps generally to the FHIR profile Identifier, we have chosen
    not to implement period (time when this identifer was in use) in order to reduce
    complexity.
    """

    # These choices taken from the FHIR valueset IdentifierUse
    # https://www.hl7.org/fhir/valueset-identifier-use.html
    USE_CHOICES = enum(
        'Usual',    # The identifier recommended for display and use in real-world interactions.
        'Official', # The identifier considered to be most trusted for the identification of this item.
        'Temp',     # A temporary identifier.
        'Old',      # The identifier id no longer considered valid, but may be relevant for search purposes.
    )

    value    = models.CharField(max_length=255, help_text="The actual identifier string")
    id_type  = models.CharField(max_length=255, help_text="Description of ID")
    use      = models.CharField(max_length=255, choices=USE_CHOICES, help_text="How should we use this ID")
    assigner = models.CharField(max_length=255, help_text="Organization that issued this ID")


class PatientContactDetail(PatientSubrecord):
    """
    A Contact detail for the patient

    While this model maps generally to the FHIR profile ContactPoint
    we have not implemented rank (order of use 1-n) or period (time when
    the contact point was/in use) in order to reduce complexity.
    """
    # These choices taken from the FHIR valueset ContactPointSystem
    SYSTEM_CHOICES = enum(
        'Phone', 'Fax', 'Email', 'Pager', 'URL', 'SMS', 'Other'
    )
    USE_CHOICES    = enum(
        'Home', 'Work', 'Temp', 'Old', 'Mobile'
    )

    system = models.CharField(max_length=50, blank=True, null=True, choices=SYSTEM_CHOICES)
    value  = models.CharField(max_length=255, blank=True, null=True)
    use    = models.CharField(max_length=255, blank=True, null=True, choices=USE_CHOICES)


class PatientContact(PatientSubrecord):
    """
    A person or orgnization that can be contacted about the patient e.g. Next of kin

    This maps broadly speaking to the FHIR Patient.contact with some exceptions for
    simplicity
    - we omit address
    - we omit gender
    - we omit Organization modelling
    - we omit period
    """
    RELATIONSHIP_CHOICES = enum(
        'Emergency Contact', 'Employer', 'Federal Agency', 'Insurance Company', 'Next-of-Kin',
        'State Agency'
    )

    name_text    = models.CharField(max_length=255, blank=True, null=True)
    relationship = models.CharField(max_length=255, blank=True, null=True, choices=RELATIONSHIP_CHOICES)
    telecom      = models.TextField(blank=True, null=True, help_text="The phone, email or other details for this contact")



class Tagging(TrackedModel, models.Model):
    _is_singleton = True
    _advanced_searchable = True

    user     = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE
    )
    episode  = models.ForeignKey(Episode, null=False, on_delete=models.CASCADE)
    archived = models.BooleanField(default=False)
    value    = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        unique_together = (('value', 'episode', 'user'))
        verbose_name = "Teams"

    def __str__(self):
        if self.user is not None:
            return 'User: %s - %s - archived: %s' % (
                self.user.username, self.value, self.archived
            )
        else:
            return "%s - archived: %s" % (self.value, self.archived)

    @staticmethod
    def get_api_name():
        return 'tagging'

    @staticmethod
    def get_display_name():
        return 'Teams'

    @staticmethod
    def get_display_template(team=None, subteam=None):
        return 'tagging.html'

    @staticmethod
    def get_form_template(team=None, subteam=None):
        return 'tagging_modal.html'

    @staticmethod
    def build_field_schema():
        # t.title is wrong, but its the better than nothing
        result = []
        for tag in patient_lists.TaggedPatientList.get_tag_names():
            result.append({
                'name': tag,
                'type': 'boolean',
                'title': tag.replace("_", " ").title()
            })
        return result



"""
Roles, access, and user models
"""




class Role(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """
    Profile for our user
    """
    HELP_RESTRICTED = "This user will only see teams that they have been " \
                      "specifically added to"
    HELP_READONLY    = "This user will only be able to read data - they " \
                       "have no write/edit permissions"
    HELP_EXTRACT     = "This user will be able to download data from " \
                       "advanced searches"
    HELP_PW          = "Force this user to change their password on the " \
                       "next login"

    user                  = models.OneToOneField(
        User, related_name='profile',
        on_delete=models.CASCADE
    )
    force_password_change = models.BooleanField(default=True,
                                                help_text=HELP_PW)
    can_extract           = models.BooleanField(default=False,
                                                help_text=HELP_EXTRACT)
    readonly              = models.BooleanField(default=False,
                                                help_text=HELP_READONLY)
    restricted_only       = models.BooleanField(default=False,
                                                help_text=HELP_RESTRICTED)
    roles                 = models.ManyToManyField(Role, blank=True)

    def to_dict(self):
        """
        Return the serialised version of this UserProfile to send to the client
        """
        return {
            'readonly'   : self.readonly,
            'can_extract': self.can_extract,
            'filters'    : [f.to_dict() for f in self.user.filter_set.all()],
            'roles'      : self.get_roles(),
            'full_name'  : self.user.get_full_name(),
            'avatar_url' : self.get_avatar_url(),
            'user_id'    : self.user.pk
        }

    def get_avatar_url(self):
        """
        Return the URL at which the avatar for this user may be found
        """
        # In order for avatars to still be useful when we have no email,
        # we want a consistent identicon that is not the same for everyone
        # e.g. users without emails don't all use the avatar for ''
        if self.user.email:
            to_hash = self.user.email.lower().encode('UTF-8')
        else:
            to_hash = self.user.username.encode('UTF-8')
        hashed = hashlib.md5(to_hash).hexdigest()
        gravatar = 'http://gravatar.com/avatar/{0}?s=80&r=g&d=identicon'
        return gravatar.format(hashed)

    def get_roles(self):
        """
        Return a roles dictionary for this user
        """
        roles = {}
        for plugin in plugins.OpalPlugin.list():
            roles.update(plugin().roles(self.user))
        roles['default'] = [r.name for r in self.roles.all()]
        return roles

    @property
    def explicit_access_only(self):
        all_roles = itertools.chain(*list(self.get_roles().values()))
        # TODO: Remove these hardcoded role anmes
        return any(r for r in all_roles if r == "scientist")


def save_profile(sender, instance, **kwargs):
    if not UserProfile.objects.filter(user=instance).exists():
        UserProfile.objects.create(user=instance)


post_save.connect(save_profile, sender=User)
