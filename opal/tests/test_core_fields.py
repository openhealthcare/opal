"""
Unittests for the opal.core.fields module
"""
from django.contrib.contenttypes.models import ContentType
from django.db import models

from opal.core.test import OpalTestCase
from opal.tests import models as test_models
from opal.models import Synonym

from opal.core import fields
from opal.core.fields import ForeignKeyOrFreeText, is_numeric


class TestIsNumeric(OpalTestCase):
    def test_is_numeric_true(self):
        numeric_fields = (
            models.IntegerField,
            models.DecimalField,
            models.BigIntegerField,
            models.FloatField,
            models.PositiveIntegerField
        )
        for field in numeric_fields:
            self.assertTrue(is_numeric(field()))

    def test_is_numeric_false(self):
        self.assertFalse(is_numeric(models.CharField))


class TestEnum(OpalTestCase):
    def test_enum(self):
        choices = (
            ('one', 'one'),
            ('2', '2'),
            ('III', 'III')
        )
        self.assertEqual(choices, fields.enum('one', '2', 'III'))

class TestForeignKeyOrFreeText(OpalTestCase):

    def test_unset_verbose_name(self):
        field = getattr(test_models.DogOwner, "dog")
        self.assertEqual(field.verbose_name, "dog")

    def test_set_verbose_name(self):
        field = getattr(test_models.HoundOwner, "dog")
        self.assertEqual(field.verbose_name, "hound")

    def test_set_help_text(self):
        field = getattr(test_models.DogOwner, "dog")
        self.assertEqual(field.help_text, "good dog")

    def test_set_max_length(self):
        field = getattr(test_models.HoundOwner, "dog")
        self.assertEqual(field.max_length, 255)

    def test_get_raises(self):
        field = ForeignKeyOrFreeText(test_models.Hat)
        result = field.__get__(self, ForeignKeyOrFreeText)
        self.assertEqual(result, 'Unknown Lookuplist Entry')

    def test_synonyms_addition(self):
        ct = ContentType.objects.get_for_model(
            test_models.Dog
        )
        alsation = test_models.Dog.objects.create(name="Alsation")
        Synonym.objects.create(
            content_type=ct, name="German Shepherd", object_id=alsation.id
        )
        _, episode = self.new_patient_and_episode_please()
        alsation_owner = test_models.DogOwner.objects.create(episode=episode)
        alsation_owner.dog = "German Shepherd"
        self.assertEqual(alsation_owner.dog, "Alsation")

    def test_multiple_addtions(self):
        ct = ContentType.objects.get_for_model(
            test_models.Dog
        )
        alsation = test_models.Dog.objects.create(name="Alsation")
        Synonym.objects.create(
            content_type=ct, name="German Shepherd", object_id=alsation.id
        )
        _, episode = self.new_patient_and_episode_please()
        alsation_owner = test_models.DogOwner.objects.create(episode=episode)
        alsation_owner.dog = "German Shepherd, Poodle"
        self.assertEqual(alsation_owner.dog, "Alsation, Poodle")
