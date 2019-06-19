"""
Models for just our tests
"""
from django.db import models as dmodels

from opal.core import fields
from opal import models
from opal.core import lookuplists
from opal.utils import AbstractBase
from opal.models import UpdatesFromDictMixin, SerialisableFields, ToDictMixin

class Birthday(models.PatientSubrecord):
    birth_date = dmodels.DateField(blank=True)
    party = dmodels.DateTimeField(blank=True, null=True)


class Dinner(models.EpisodeSubrecord):
    food = dmodels.CharField(max_length=256, null=True, blank=True)
    time = dmodels.TimeField(blank=True, null=True)


class Hat(lookuplists.LookupList):
    pass


class EtherialHat(lookuplists.LookupList):
    class Meta:
        abstract = True


class GhostHat(EtherialHat):
    pass


class HatWearer(models.EpisodeSubrecord):
    _sort = 'name'
    name = dmodels.CharField(max_length=200)
    hats = dmodels.ManyToManyField(Hat, related_name="hat_wearers")
    wearing_a_hat = dmodels.BooleanField(default=True)

    class Meta:
        verbose_name = 'Wearer of Hats'


class EntitledHatWearer(models.EpisodeSubrecord):
    _advanced_searchable = False
    _exclude_from_extract = True

    name = dmodels.CharField(max_length=200)

    class Meta:
        verbose_name = 'Entitled Wearer of Hats'


class InvisibleHatWearer(models.EpisodeSubrecord):
    _exclude_from_subrecords = True

    class Meta:
        verbose_name = 'Invisible Wearer of Hats'

    name = dmodels.CharField(max_length=200)
    wearing_a_hat = dmodels.BooleanField(default=True)


class AbstractHatWearer(models.EpisodeSubrecord, AbstractBase):
    name = dmodels.CharField(max_length=200)
    wearing_a_hat = dmodels.BooleanField(default=True)


class HouseOwner(models.PatientSubrecord):
    pass


class House(dmodels.Model):
    address = dmodels.CharField(max_length=200)
    house_owner = dmodels.ForeignKey(
        HouseOwner, null=True, blank=True, on_delete=dmodels.CASCADE
    )


class Dog(lookuplists.LookupList):
    pass


class DogOwner(models.EpisodeSubrecord):
    name = dmodels.CharField(
        max_length=200, default="Catherine"
    )
    dog = fields.ForeignKeyOrFreeText(
        Dog, default="spaniel", help_text="good dog"
    )
    least_favourite_dog = fields.ForeignKeyOrFreeText(Dog, related_name='hated_dogs')
    ownership_start_date = dmodels.DateField(blank=True, null=True, verbose_name="OSD")


class HoundOwner(models.EpisodeSubrecord):
    name = dmodels.CharField(max_length=200, default="Philipa")
    dog = fields.ForeignKeyOrFreeText(Dog, verbose_name="hound", default="spaniel")


class FavouriteDogs(models.PatientSubrecord):
    dogs = dmodels.ManyToManyField(Dog, related_name='favourite_dogs')


class FavouriteNumber(models.PatientSubrecord):
    number = dmodels.IntegerField(blank=True, null=True)


class InvisibleDog(models.PatientSubrecord):
    _exclude_from_subrecords = True
    name = dmodels.CharField(max_length=200, default="Catherine")


class AbstractDog(models.PatientSubrecord, AbstractBase):
    name = dmodels.CharField(max_length=200)


class AbstractDogOwner(models.EpisodeSubrecord):
    name = dmodels.CharField(
        max_length=200, default="Catherine"
    )
    dog = fields.ForeignKeyOrFreeText(
        Dog, default="spaniel", help_text="good dog"
    )

    class Meta:
        abstract = True


class SpanielOwner(AbstractDogOwner):
    pass


class CockerSpanielOwner(SpanielOwner):
    class Meta:
        proxy = True


class SensitiveDogOwner(models.EpisodeSubrecord):
    name = dmodels.CharField(
        max_length=200, default="Catherine"
    )
    dog = fields.ForeignKeyOrFreeText(
        Dog, case_sensitive=True
    )


class Colour(models.EpisodeSubrecord):
    _advanced_searchable = False
    _exclude_from_extract = True
    _angular_service = 'Colour'
    _icon = "fa fa-comments"

    name = dmodels.CharField(max_length=200, null=True, blank=True)


class PatientColour(models.PatientSubrecord):
    name = dmodels.CharField(max_length=200, blank=True, null=True)
    _exclude_from_extract = True


class FamousLastWords(models.PatientSubrecord):
    _is_singleton = True
    _read_only = True

    words = dmodels.CharField(verbose_name="only words", max_length=200, blank=True, null=True)


class EpisodeName(models.EpisodeSubrecord):
    _is_singleton = True

    name = dmodels.CharField(max_length=200, blank=True, null=True)


COLOUR_CHOICES = (
    ('purple', 'purple'),
    ('yellow', 'yellow'),
    ('blue', 'blue'),
)


class FavouriteColour(models.PatientSubrecord):
    _is_singleton = True
    name = dmodels.CharField(
        max_length=200, blank=True, null=True, choices=COLOUR_CHOICES,
        help_text="orange is the new black"
    )


class ExternalSubRecord(
    models.EpisodeSubrecord,
    models.ExternallySourcedModel,
):
    name = dmodels.CharField(max_length=200, blank=True, null=True)


class Demographics(models.Demographics):
    _is_singleton = True
    pid_fields = 'first_name', 'surname',


class Location(models.Location):
    _is_singleton = True


class SymptomComplex(models.SymptomComplex):
    pass


class PatientConsultation(models.PatientConsultation):
    pass


class DatingModel(UpdatesFromDictMixin, dmodels.Model):
    datetime = dmodels.DateTimeField()
    consistency_token = None


class UpdatableModelInstance(UpdatesFromDictMixin, dmodels.Model):
    foo = dmodels.CharField(max_length=200, blank=True, null=True)
    bar = dmodels.CharField(max_length=200, blank=True, null=True)
    pid = dmodels.CharField(max_length=200, blank=True, null=True)
    hatty = fields.ForeignKeyOrFreeText(Hat)
    pid_fields = 'pid', 'hatty'


class GetterModel(ToDictMixin, dmodels.Model):
    foo = dmodels.CharField(max_length=200, blank=True, null=True)

    def get_foo(self, user):
        return "gotten"


class SerialisableModel(SerialisableFields, dmodels.Model):
    pid = dmodels.CharField(max_length=200, blank=True, null=True)
    hatty = fields.ForeignKeyOrFreeText(Hat)
