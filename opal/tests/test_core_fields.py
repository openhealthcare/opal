"""
Unittests for the opal.core.fields module
"""
from unittest import mock
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

    def test_unset_value(self):
        patient, episode = self.new_patient_and_episode_please()
        demographics = test_models.Demographics(patient=patient)
        demographics.save()
        self.assertEqual('', demographics.title)

    def test_get_default_when_callable(self):
        field = ForeignKeyOrFreeText(test_models.Demographics, default=lambda: 'Nope')
        self.assertEqual('Nope', field.get_default())

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

    def test_case_insensitive_fk(self):
        alsation = test_models.Dog.objects.create(name="Alsation")
        _, episode = self.new_patient_and_episode_please()
        alsation_owner = test_models.SpanielOwner.objects.create(
            episode=episode
        )
        alsation_owner.dog = alsation.name.lower()
        alsation_owner.save()
        self.assertEqual(alsation_owner.dog, alsation.name)
        self.assertEqual(alsation_owner.dog_fk_id, alsation.id)

    def test_case_insensitive_synonym(self):
        ct = ContentType.objects.get_for_model(
            test_models.Dog
        )
        alsation = test_models.Dog.objects.create(name="Alsation")
        Synonym.objects.create(
            content_type=ct,
            name="German Shepherd",
            object_id=alsation.id
        )
        _, episode = self.new_patient_and_episode_please()
        alsation_owner = test_models.SpanielOwner.objects.create(
            episode=episode
        )
        alsation_owner.dog = alsation.name.lower()
        alsation_owner.save()
        alsation_owner.dog = "german shepherd"
        self.assertEqual(alsation_owner.dog, "Alsation")
        self.assertEqual(alsation_owner.dog_fk_id, alsation.id)

    def test_case_sensitive_fk(self):
        alsation = test_models.Dog.objects.create(name="Alsation")
        _, episode = self.new_patient_and_episode_please()
        alsation_owner = test_models.SensitiveDogOwner.objects.create(
            episode=episode
        )
        alsation_owner.dog = alsation.name.lower()
        alsation_owner.save()
        self.assertEqual(alsation_owner.dog, alsation.name.lower())
        self.assertEqual(alsation_owner.dog_ft, alsation.name.lower())

        alsation_owner.dog = alsation.name
        alsation_owner.save()
        self.assertEqual(alsation_owner.dog, alsation.name)
        self.assertEqual(alsation_owner.dog_fk_id, alsation.id)

    def test_case_sensitive_synonym(self):
        ct = ContentType.objects.get_for_model(
            test_models.Dog
        )
        alsation = test_models.Dog.objects.create(name="Alsation")
        Synonym.objects.create(
            content_type=ct,
            name="German Shepherd",
            object_id=alsation.id
        )
        _, episode = self.new_patient_and_episode_please()
        alsation_owner = test_models.SensitiveDogOwner.objects.create(
            episode=episode
        )
        alsation_owner.dog = alsation.name.lower()
        alsation_owner.save()
        alsation_owner.dog = "german shepherd"
        self.assertEqual(alsation_owner.dog, "german shepherd")
        self.assertEqual(alsation_owner.dog_ft, "german shepherd")

        alsation_owner.dog = "German Shepherd"
        self.assertEqual(alsation_owner.dog, alsation.name)
        self.assertEqual(alsation_owner.dog_fk_id, alsation.id)

    def test_delete(self):
        alsation = test_models.Dog.objects.create(name="Alsation")
        _, episode = self.new_patient_and_episode_please()
        alsation_owner = test_models.DogOwner.objects.create(episode=episode)
        alsation_owner.dog = alsation.name
        alsation_owner.save()

        # sanity checks that we're testing the right thing
        self.assertEqual(alsation_owner.dog_ft, '')
        self.assertEqual(alsation_owner.dog_fk.id, alsation.id)

        alsation.delete()

        alsation_owner = test_models.DogOwner.objects.get()

        self.assertEqual(
            alsation_owner.dog, "Alsation"
        )

        self.assertEqual(
            alsation_owner.dog_ft, "Alsation"
        )

    def test_delete_with_abstract(self):
        alsation = test_models.Dog.objects.create(name="Alsation")
        _, episode = self.new_patient_and_episode_please()
        alsation_owner = test_models.SpanielOwner.objects.create(episode=episode)
        alsation_owner.dog = alsation.name
        alsation_owner.save()

        # sanity checks that we're testing the right thing
        self.assertEqual(alsation_owner.dog_ft, '')
        self.assertEqual(alsation_owner.dog_fk.id, alsation.id)

        alsation.delete()

        alsation_owner = test_models.SpanielOwner.objects.get()

        self.assertEqual(
            alsation_owner.dog, "Alsation"
        )

        self.assertEqual(
            alsation_owner.dog_ft, "Alsation"
        )

    def test_delete_with_proxy(self):
        alsation = test_models.Dog.objects.create(name="Alsation")
        _, episode = self.new_patient_and_episode_please()
        alsation_owner = test_models.CockerSpanielOwner.objects.create(
            episode=episode
        )
        alsation_owner.dog = alsation.name
        alsation_owner.save()

        # sanity checks that we're testing the right thing
        self.assertEqual(alsation_owner.dog_ft, '')
        self.assertEqual(alsation_owner.dog_fk.id, alsation.id)

        alsation.delete()

        alsation_owner = test_models.CockerSpanielOwner.objects.get()

        self.assertEqual(
            alsation_owner.dog, "Alsation"
        )

        self.assertEqual(
            alsation_owner.dog_ft, "Alsation"
        )

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
