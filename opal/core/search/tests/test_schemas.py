from django.test import TestCase
from mock import patch, MagicMock, PropertyMock
from opal.tests.models import Colour


from opal.core.search import schemas

colour_serialized = dict(
    name='colour',
    icon="fa fa-comments",
    display_name='Colour',
    description="I like blue",
    fields=[
        {'model': 'Colour',
         'lookup_list': None,
         'default': None,
         'enum': None,
         'description': None,
         'name': 'consistency_token',
         'title': 'Consistency Token',
         'type_display_name': 'Text Field',
         'type': 'token'},
        {'model': 'Colour',
         'lookup_list': None,
         'type': 'date_time',
         'name': 'created',
         'default': None,
         'enum': None,
         'type_display_name': 'Date & Time',
         'description': None,
         'title': 'Created'},
        {'model': 'Colour',
         'lookup_list': None,
         'default': None,
         'name': 'created_by_id',
         'title': 'Created By',
         'enum': None,
         'description': 'One of the Users',
         'type': 'forei',
         'type_display_name': 'Relationship',
         },
        {'model': 'Colour',
         'lookup_list': None,
         'default': None,
         'enum': None,
         'description': None,
         'name': 'name',
         'title': 'Name',
         'type': 'string',
         'type_display_name': 'Text Field',
         },
        {'model': 'Colour',
         'lookup_list': None,
         'type': 'date_time',
         'name': 'updated',
         'default': None,
         'enum': None,
         'description': None,
         'type_display_name': 'Date & Time',
         'title': 'Updated'},
        {'model': 'Colour',
         'lookup_list': None,
         'default': None,
         'enum': None,
         'type_display_name': 'Relationship',
         'description': 'One of the Users',
         'name': 'updated_by_id',
         'title': 'Updated By',
         'type': 'forei'},
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
    'description': None,
    'name': 'episode',
}


@patch('opal.core.search.schemas.subrecords')
@patch('opal.core.search.schemas.SearchRule')
class ExtractSchemaTestCase(TestCase):
    def test_extract_schema(self, SearchRule, subrecords):
        from opal.core.search.search_rule import EpisodeQuery
        SearchRule.list.return_value = [EpisodeQuery]
        subrecords.return_value = [Colour]

        with patch.object(
            EpisodeQuery.fields[2], "enum", new_callable=PropertyMock
        ) as all_teams:
            all_teams.return_value = []
            extract_schema = schemas.extract_search_schema()
        self.assertEqual(colour_serialized, extract_schema[0])
        self.assertEqual(episode_serialised, extract_schema[1])

    def test_rules_are_appended(self, SearchRule, subrecords):
        subrecords.return_value = []
        search_rule = MagicMock()
        SearchRule.list.return_value = [search_rule]
        rule_to_dicted = {"display_name": "Some Search Rule"}
        search_rule().to_dict.return_value = rule_to_dicted
        extract_schema = schemas.extract_search_schema()
        self.assertEqual([rule_to_dicted], extract_schema)


class ExtractDownloadSchemaForModelTestCase(TestCase):
    def test_extract_download_schema_for_model(self):
        with patch.object(
            Colour, "_get_fieldnames_to_extract"
        ) as gfte:
            gfte.return_value = "name"
            result = schemas.extract_download_schema_for_model(Colour)
            expected = dict(
                fields=[{
                    'model': 'Colour',
                    'lookup_list': None,
                    'default': None,
                    'enum': None,
                    'description': None,
                    'name': 'name',
                    'title': 'Name',
                    'type': 'string',
                    'type_display_name': 'Text Field',
                }],
                name='colour',
                icon="fa fa-comments",
                display_name='Colour',
                description="I like blue",
            )
            self.assertEqual(result, expected)
