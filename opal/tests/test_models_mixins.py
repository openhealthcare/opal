"""
Unittests for mixins in opal.models
"""
import datetime
import pytz

from django.db import models
from unittest.mock import patch

from opal.core import exceptions
from opal.core.fields import ForeignKeyOrFreeText
from opal.core.test import OpalTestCase
from opal.tests import models as test_models
from opal.tests.models import (
    DatingModel, Dinner, UpdatableModelInstance, GetterModel, SerialisableModel
)
from opal.models import (
    UpdatesFromDictMixin, SerialisableFields, ToDictMixin
)




class SerialisableFieldsTestCase(OpalTestCase):

    def test_get_fieldnames(self):
        names = SerialisableModel._get_fieldnames_to_serialize()
        expected = set([
            'id',
            'pid',
            'hatty',
        ])
        self.assertEqual(expected, set(names))

    def test_get_field_type(self):
        self.assertEqual(models.ForeignKey, SerialisableModel._get_field_type('patient_id'))

    def test_get_human_readable_type_boolean(self):
        with patch.object(SerialisableModel, "_get_field") as get_field:
            get_field.return_value = models.BooleanField()
            self.assertEqual(
                SerialisableModel.get_human_readable_type("tree"),
                "Either True or False",
            )

    def test_get_human_readable_type_null_boolean(self):
            with patch.object(SerialisableModel, "_get_field") as get_field:
                get_field.return_value = models.NullBooleanField()
                self.assertEqual(
                    SerialisableModel.get_human_readable_type("tree"),
                    "Either True, False or None",
                )

    def test_get_human_readable_type_date_field(self):
            with patch.object(SerialisableModel, "_get_field") as get_field:
                get_field.return_value = models.DateField()
                self.assertEqual(
                    SerialisableModel.get_human_readable_type("tree"),
                    "Date",
                )

    def test_get_human_readable_type_datetime_field(self):
            with patch.object(SerialisableModel, "_get_field") as get_field:
                get_field.return_value = models.DateTimeField()
                self.assertEqual(
                    SerialisableModel.get_human_readable_type("tree"),
                    "Date & Time",
                )

    def test_get_human_readable_type_numeric_field(self):
        numeric_fields = [
            models.AutoField,
            models.BigIntegerField,
            models.IntegerField,
            models.FloatField,
            models.DecimalField
        ]
        for numeric_field in numeric_fields:
            with patch.object(SerialisableModel, "_get_field") as get_field:
                get_field.return_value = numeric_field()
                self.assertEqual(
                    SerialisableModel.get_human_readable_type("tree"),
                    "Number"
                )

    def test_get_human_readable_type_reverse_foreign_key_field(self):
        self.assertEqual(
            test_models.HatWearer.get_human_readable_type("created_by"),
            "One of the Users"
        )

    def test_get_human_readable_type_many_to_many_field(self):
        self.assertEqual(
            test_models.HatWearer.get_human_readable_type("hats"),
            "Some of the Hats"
        )

    def test_build_field_schema(self):
        schema = SerialisableModel.build_field_schema()
        expected = [
            {
                'model': 'SerialisableModel',
                'description': None,
                'enum': None,
                'lookup_list': None,
                'type': 'string',
                'name': 'pid',
                'default': None,
                'title': u'Pid'
            },
            {
                'model': 'SerialisableModel',
                'description': None,
                'enum': None,
                'lookup_list': 'hat',
                'type': 'string',
                'name': 'hatty',
                'default': None,
                'title': 'Hatty'
            }
        ]
        self.assertEqual(schema, expected)

    def test_build_schema_for_field_name(self):
        expected_fields = [
            "name",
            "title",
            "type",
            "lookup_list",
            "default",
            "model",
            "description",
            "enum"
        ]

        result = test_models.Colour.build_schema_for_field_name("name")
        self.assertEqual(set(result), set(expected_fields))

    def test_get_lookup_list_api_name(self):
        result = test_models.HoundOwner.get_lookup_list_api_name("dog")
        self.assertEqual(result, "dog")

    def test_get_lookup_list_many_to_many_api_name(self):
        result = test_models.HatWearer.get_lookup_list_api_name("hats")
        self.assertEqual(result, "hat")

    def test_get_lookup_list_uses_api_name(self):
        with patch.object(test_models.Dog, "get_api_name") as get_api_name:
            get_api_name.return_value = "hound"
            result = test_models.HoundOwner.get_lookup_list_api_name("dog")
            self.assertEqual(result, "hound")
            get_api_name.assert_called_once_with()

    def test_get_lookup_list_api_name_when_none(self):
        # when we're not in a M2M field or a FK or FT field then
        # then we should just return None
        result = test_models.HoundOwner.get_lookup_list_api_name("name")
        self.assertIsNone(result)


class ToDictMixinTestCase(OpalTestCase):
    def setUp(self):
        self.model_instance = GetterModel(foo="blah")

    def test_to_dict(self):
        patient, episode = self.new_patient_and_episode_please()
        dinner = Dinner.objects.create(episode=episode)
        as_dict = dinner.to_dict(self.user)
        expected = {
            'food':              None,
            'time':              None,
            'id':                dinner.id,
            'episode_id':        episode.id,
            'consistency_token': '',
            'created':           None,
            'created_by_id':     None,
            'updated':           None,
            'updated_by_id':     None
        }
        self.assertEqual(expected, as_dict)

    def test_to_dict_empty_fk_ft_fields(self):
        patient, episode = self.new_patient_and_episode_please()
        demographics = patient.demographics_set.get()
        as_dict = demographics.to_dict(self.user)
        for field in ['title', 'sex', 'ethnicity']:
            self.assertEqual('', as_dict[field])

    def test_getter_is_used(self):
        self.assertEqual(
            self.model_instance.to_dict(self.user),
            dict(foo="gotten", id=None)
        )


class UpdatesFromDictMixinTestCase(OpalTestCase):
    def setUp(self):
        self.model = UpdatableModelInstance

    def test_get_fieldnames_to_serialize(self):
        expected = ['id', 'foo', 'bar', 'pid', 'hatty']
        self.assertEqual(expected, self.model._get_fieldnames_to_serialize())

    def test_get_fieldnames_to_extract(self):
        expected = ['id', 'foo', 'bar']
        self.assertEqual(expected, self.model._get_fieldnames_to_extract())

    def test_get_fieldnames_to_extract_fkorft_438(self):
        # Regression test for https://github.com/opal/issues/438
        fnames = self.model._get_fieldnames_to_extract()
        self.assertFalse('hatty_fk_id' in fnames)
        self.assertFalse('hatty_ft' in fnames)

    def test_get_field_type_unknown(self):
        with self.assertRaises(exceptions.UnexpectedFieldNameError):
            self.model._get_field_type('not_a_real_field')

    def test_update_from_dict_datetime(self):
        data = {'datetime': '04/11/1953 12:20:00'}
        expected = datetime.datetime(1953, 11, 4, 12, 20, 0, 0, pytz.UTC)
        instance = DatingModel()

        with patch.object(instance, '_get_field_type') as mock_type:
            with patch.object(instance, 'save'):
                mock_type.return_value = models.DateTimeField

                result = instance.update_from_dict(data, None)
                self.assertEqual(expected, instance.datetime)

    def test_update_from_dict_no_consistency_token(self):
        instance = UpdatableModelInstance(foo='foo', bar='bar')
        instance.set_consistency_token()
        instance.save()
        data = {'foo': 'Hah', 'bar': 'Hah'}
        with self.assertRaises(exceptions.MissingConsistencyTokenError):
            instance.update_from_dict(data, self.user)
