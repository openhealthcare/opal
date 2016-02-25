"""
Tests for schema utilities
"""
from django.test import TestCase
from mock import patch

from opal.core import schemas
from opal.tests.models import Colour

colour_serialized = dict(
    name='colour',
    display_name='Colour',
    single=False,
    advanced_searchable=False,
    fields=[
        {'lookup_list': None,
         'type': 'date_time',
         'name': 'created',
         'title': 'Created'},
        {'lookup_list': None,
         'type': 'date_time',
         'name': 'updated',
         'title': 'Updated'},
        {'lookup_list': None,
         'name': 'created_by_id',
         'title': 'Created By Id',
         'type': 'forei'},
        {'lookup_list': None,
         'name': 'updated_by_id',
         'title': 'Updated By Id',
         'type': 'forei'},
        {'lookup_list': None,
         'name': 'consistency_token',
         'title': 'Consistency Token',
         'type': 'token'},
        {'lookup_list': None,
         'name': 'name',
         'title': 'Name',
         'type': 'string'},
    ]
)

tagging_serialized = {
    'fields': [],
    'single': True,
    'display_name': 'Teams',
    'name': 'tagging',
    'advanced_searchable': True,
}


class SerializeModelTestCase(TestCase):
    def test_serialize(self):
        self.assertEqual(colour_serialized, schemas.serialize_model(Colour))


class SerializeSchemaTestCase(TestCase):
    def test_serialize(self):
        self.assertEqual(
            [colour_serialized, colour_serialized],
            schemas.serialize_schema([Colour, Colour])
        )


class ListRecordsTestCase(TestCase):
    @patch('opal.core.schemas.subrecords')
    @patch('opal.core.schemas.models.Tagging.build_field_schema')
    def test_list_records(self, tagging, subrecords):
        subrecords.return_value = [Colour]
        tagging.return_value = []
        expected = {
            'tagging': tagging_serialized,
            'colour': colour_serialized
        }
        self.assertEqual(expected, schemas.list_records())


class ExtractSchemaTestCase(TestCase):
    @patch('opal.core.schemas.subrecords')
    @patch('opal.core.schemas.models.Tagging.build_field_schema')
    def test_list_records(self, tagging, subrecords):
        subrecords.return_value = [Colour]
        tagging.return_value = []
        self.assertEqual(tagging_serialized, schemas.extract_schema()[0])
        self.assertEqual(colour_serialized, schemas.extract_schema()[1])
