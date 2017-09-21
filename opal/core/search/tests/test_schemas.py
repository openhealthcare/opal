from django.test import TestCase
from mock import patch
from opal.tests.models import Colour


from opal.core.search import schemas

colour_serialized = dict(
    name='colour',
    icon="fa fa-comments",
    display_name='Colour',
    single=False,
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
         'description': 'One of the Users',
         'type': 'forei'},
        {'model': 'Colour',
         'lookup_list': None,
         'default': None,
         'enum': None,
         'description': 'One of the Users',
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

episode_serialised = {
    'fields': [
        {
            'enum': None,
            'lookup_list': None,
            'name': 'start',
            'title': 'Start',
            'type': 'date_time',
            'type_display_name': 'Date & Time',
            'description': "Episode Start"
        },
        {
            'enum': None,
            'lookup_list': None,
            'name': 'end',
            'title': 'End',
            'type': 'date_time',
            'type_display_name': 'Date & Time',
            'description': "Episode End"
        },
        {
            'description': 'The team(s) related to an episode of care',
            'enum': [],
            'lookup_list': None,
            'name': 'team',
            'title': 'Team',
            'type_display_name': 'Text Field',
            'type': 'many_to_many_multi_select'
         }
    ],
    'display_name': 'Episode',
    'name': 'episode',
}


class ExtractSchemaTestCase(TestCase):
    @patch('opal.core.search.schemas.subrecords')
    def test_extract_schema(self, subrecords):
        subrecords.return_value = [Colour]

        self.assertEqual(colour_serialized, schemas.extract_schema()[0])
        self.assertEqual(episode_serialised, schemas.extract_schema()[1])
