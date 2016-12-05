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

from opal.models import (
    UpdatesFromDictMixin, SerialisableFields, ToDictMixin
)


class DatingModel(UpdatesFromDictMixin, models.Model):
    datetime = models.DateTimeField()
    consistency_token = None


class UpdatableModelInstance(UpdatesFromDictMixin, models.Model):
    foo = models.CharField(max_length=200, blank=True, null=True)
    bar = models.CharField(max_length=200, blank=True, null=True)
    pid = models.CharField(max_length=200, blank=True, null=True)
    hatty = ForeignKeyOrFreeText(test_models.Hat)
    pid_fields = 'pid', 'hatty'


class GetterModel(ToDictMixin, models.Model):
    foo = models.CharField(max_length=200, blank=True, null=True)

    def get_foo(self, user):
        return "gotten"


class SerialisableModel(SerialisableFields, models.Model):
    pid = models.CharField(max_length=200, blank=True, null=True)
    hatty = ForeignKeyOrFreeText(test_models.Hat)


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

    def test_build_field_schema(self):
        schema = SerialisableModel.build_field_schema()
        expected = [
            {
                'model': 'SerialisableModel',
                'lookup_list': None,
                'type': 'string',
                'name': 'pid',
                'default': None,
                'title': u'Pid'
            },
            {
                'model': 'SerialisableModel',
                'lookup_list': 'hat',
                'type': 'string',
                'name': 'hatty',
                'default': None,
                'title': 'Hatty'
            }
        ]
        self.assertEqual(schema, expected)


class ToDictMixinTestCase(OpalTestCase):
    def setUp(self):
        self.model_instance = GetterModel(foo="blah")

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
