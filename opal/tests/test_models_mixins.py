"""
Unittests for opal.models.mixins
"""
from django.db import models
from opal.core.test import OpalTestCase

from opal.models import mixins

class UpdatesFromDictMixin(OpalTestCase):
    def setUp(self):
        
        class UpdatableModel(mixins.UpdatesFromDictMixin, models.Model):
            foo = models.CharField(max_length=200, blank=True, null=True)
            bar = models.CharField(max_length=200, blank=True, null=True)
            pid = models.CharField(max_length=200, blank=True, null=True)

            pid_fields = 'pid',

        self.model = UpdatableModel

    def test_get_fieldnames_to_serialize(self):
        expected = ['id', 'foo', 'bar', 'pid']
        self.assertEqual(expected, self.model._get_fieldnames_to_serialize())

    def test_get_fieldnames_to_extract(self):
        expected = ['id', 'foo', 'bar']
        self.assertEqual(expected, self.model._get_fieldnames_to_extract())
