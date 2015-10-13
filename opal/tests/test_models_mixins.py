"""
Unittests for opal.models.mixins
"""
import datetime
import pytz

from django.db import models
from mock import patch
from opal.core.test import OpalTestCase

from opal.models import UpdatesFromDictMixin


class DatingModel(UpdatesFromDictMixin, models.Model):
    datetime = models.DateTimeField()
    consistency_token = None


class UpdatableModelInstance(UpdatesFromDictMixin, models.Model):
    foo = models.CharField(max_length=200, blank=True, null=True)
    bar = models.CharField(max_length=200, blank=True, null=True)
    pid = models.CharField(max_length=200, blank=True, null=True)

    pid_fields = 'pid',


class UpdatesFromDictMixin(OpalTestCase):
    def setUp(self):
        self.model = UpdatableModelInstance

    def test_get_fieldnames_to_serialize(self):
        expected = ['id', 'foo', 'bar', 'pid']
        self.assertEqual(expected, self.model._get_fieldnames_to_serialize())

    def test_get_fieldnames_to_extract(self):
        expected = ['id', 'foo', 'bar']
        self.assertEqual(expected, self.model._get_fieldnames_to_extract())

    def test_update_from_dict_datetime(self):
        data = {'datetime': '1953-11-04 12:20+0000'}
        expected = datetime.datetime(1953, 11, 4, 12, 20, 0, 0, pytz.UTC)
        instance = DatingModel()

        with patch.object(instance, '_get_field_type') as mock_type:
            with patch.object(instance, 'save'):
                mock_type.return_value = models.DateTimeField

                instance.update_from_dict(data, None)
                self.assertEqual(expected, instance.datetime)
