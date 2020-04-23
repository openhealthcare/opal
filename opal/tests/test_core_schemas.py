"""
Tests for schema utilities
"""
from django.test import TestCase
from unittest.mock import patch

from opal.core import schemas
from opal.tests.models import Colour, HatWearer, FamousLastWords

colour_serialized = dict(
    name='colour',
    icon="fa fa-comments",
    display_name='Colour',
    single=False,
    advanced_searchable=False,
    angular_service='Colour',
    form_url=u'/templates/forms/colour.html',
    fields=[
        {'model': 'Colour',
         'lookup_list': None,
         'type': 'date_time',
         'name': 'created',
         'default': None,
         'enum': None,
         'description': None,
         'title': 'Created'},
        {'model': 'Colour',
         'lookup_list': None,
         'type': 'date_time',
         'name': 'updated',
         'default': None,
         'enum': None,
         'description': None,
         'title': 'Updated'},
        {'model': 'Colour',
         'lookup_list': None,
         'default': None,
         'name': 'created_by_id',
         'title': 'Created By',
         'enum': None,
         'description': None,
         'type': 'forei'},
        {'model': 'Colour',
         'lookup_list': None,
         'default': None,
         'enum': None,
         'description': None,
         'name': 'updated_by_id',
         'title': 'Updated By',
         'type': 'forei'},
        {'model': 'Colour',
         'lookup_list': None,
         'default': None,
         'enum': None,
         'description': None,
         'name': 'consistency_token',
         'title': 'Consistency Token',
         'type': 'token'},
        {'model': 'Colour',
         'lookup_list': None,
         'default': None,
         'enum': None,
         'description': None,
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

episode_serialised = {
    'fields': [
        {
            'enum': None,
            'lookup_list': None,
            'name': 'start',
            'title': 'Start',
            'type': 'date_time',
            'description': "Episode Start"
        },
        {
            'enum': None,
            'lookup_list': None,
            'name': 'end',
            'title': 'End',
            'type': 'date_time',
            'description': "Episode End"
        }
    ],
    'display_name': 'Episode',
    'name': 'episode',
    'advanced_searchable': True,
}


class SerializeModelTestCase(TestCase):
    def test_serialize(self):
        self.assertEqual(colour_serialized, schemas.serialize_model(Colour))

    def test_serialize_sort(self):
        self.assertEqual('name', schemas.serialize_model(HatWearer)['sort'])

    def test_serialize_readonly(self):
        self.assertEqual(True, schemas.serialize_model(FamousLastWords)['readOnly'])


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
    def test_extract_schema(self, tagging, subrecords):
        subrecords.return_value = [Colour]
        tagging.return_value = []
        self.assertEqual(episode_serialised, schemas.extract_schema()[0])
        self.assertEqual(tagging_serialized, schemas.extract_schema()[1])
        self.assertEqual(colour_serialized, schemas.extract_schema()[2])
