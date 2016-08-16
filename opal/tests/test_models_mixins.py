"""
Unittests for opal.models.mixins
"""
import datetime
import pytz

from django.db import models
from mock import patch

from opal.core import exceptions
from opal.core.fields import ForeignKeyOrFreeText
from opal.core.test import OpalTestCase
from opal.tests import models as test_models

from opal.models import UpdatesFromDictMixin, SerialisableFields


class DatingModel(UpdatesFromDictMixin, models.Model):
    datetime = models.DateTimeField()
    consistency_token = None


class UpdatableModelInstance(UpdatesFromDictMixin, models.Model):
    foo = models.CharField(max_length=200, blank=True, null=True)
    bar = models.CharField(max_length=200, blank=True, null=True)
    pid = models.CharField(max_length=200, blank=True, null=True)
    hatty = ForeignKeyOrFreeText(test_models.Hat)

    pid_fields = 'pid', 'hatty'


class SerialisableFieldsTestCase(OpalTestCase):
    def test_get_fieldnames_to_serialise_with_many_to_many(self):
        self.assertTrue(
            isinstance(test_models.HatWearer(), SerialisableFields)
        )
        names = test_models.HatWearer._get_fieldnames_to_serialize()
        expected = [
            'id',
            'created',
            'updated',
            'created_by_id',
            'updated_by_id',
            'consistency_token',
            'episode_id',
            'name',
            'wearing_a_hat',
            'hats'
        ]
        self.assertEqual(expected, names)

    def test_get_fieldnames_to_serialise_with_fk_or_ft(self):
        names = test_models.HoundOwner._get_fieldnames_to_serialize()
        expected = [
            'id',
            'created',
            'updated',
            'created_by_id',
            'updated_by_id',
            'consistency_token',
            'episode_id',
            'name',
            u'dog_fk_id',
            'dog_ft',
            'dog'
        ]
        self.assertEqual(expected, names)


class UpdatesFromDictMixinTestCase(OpalTestCase):
    def setUp(self):
        self.model = UpdatableModelInstance

    def test_get_fieldnames_to_serialize(self):
        expected = ['id', 'foo', 'bar', 'pid', 'hatty_fk_id', 'hatty_ft', 'hatty']
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
