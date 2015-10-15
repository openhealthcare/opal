"""
unittests for opal.core.search.queries
"""
from mock import patch

from opal.models import Patient, Team
from opal.core.test import OpalTestCase
from datetime import date

from opal.core.search import queries


class DatabaseQueryTestCase(OpalTestCase):
    DATE_OF_BIRTH = date(day=27, month=1, year=1977)
    DATE_OF_EPISODE = date(day=1, month=2, year=2015)

    def setUp(self):
        self.patient = Patient.objects.create()
        self.episode = self.patient.create_episode(
            category="testepisode",
        )
        self.episode.date_of_episode = self.DATE_OF_EPISODE
        self.episode.save()
        self.demographics = self.patient.demographics_set.get()
        self.demographics.name = "Sally Stevens"
        self.demographics.gender = "Female"
        self.demographics.hospital_number = "0"
        self.demographics.date_of_birth = self.DATE_OF_BIRTH
        self.demographics.save()

        self.general_team, _ = Team.objects.get_or_create(
            name='general', title='General Team')
        self.restricted_team, _ = Team.objects.get_or_create(
            name='restricted', title='Restricted Team', restricted=True)
        self.name_criteria = [
            {
                u'column': u'demographics',
                u'field': u'Name',
                u'combine': u'and',
                u'query': u'Sally Stevens',
                u'queryType': u'Equals'
            }
        ]

    def test_filter_restricted_only_user(self):
        self.user.profile.restricted_only   = True
        self.user.profile.save()
        self.patient.create_episode(category='nonsensecategory')
        query = queries.DatabaseQuery(self.user, self.name_criteria)
        self.assertEqual([], query.get_episodes())
        self.episode.set_tag_names(['restricted'], self.user)
        with patch.object(queries.models.Team, 'restricted_teams') as mock_restrict:
            mock_restrict.return_value = [self.restricted_team]
            self.assertEqual([self.episode], query.get_episodes())

    def test_filter_out_restricted_teams(self):
        query = queries.DatabaseQuery(self.user, self.name_criteria)
        self.episode.set_tag_names(['restricted'], self.user)
        self.assertEqual([], query.get_episodes())

    def test_filter_in_restricted_teams(self):
        query = queries.DatabaseQuery(self.user, self.name_criteria)
        self.episode.set_tag_names(['restricted'], self.user)
        with patch.object(queries.models.Team, 'restricted_teams') as mock_restrict:
            mock_restrict.return_value = [self.restricted_team]
            self.assertEqual([self.episode], query.get_episodes())

    def test_get_episodes(self):
        query = queries.DatabaseQuery(self.user, self.name_criteria)
        self.assertEqual([self.episode], query.get_episodes())

    def test_get_episodes_searching_ft_or_fk_field(self):
        criteria = [
            {
                u'column': u'demographics',
                u'field': u'Gender',
                u'combine': u'and',
                u'query': u'Female',
                u'queryType': u'Equals'
            }
        ]
        query = queries.DatabaseQuery(self.user, criteria)
        self.assertEqual([self.episode], query.get_episodes())

    def test_get_patient_summaries(self):
        query = queries.DatabaseQuery(self.user, self.name_criteria)
        summaries = query.get_patient_summaries()
        expected = [{
            'id': self.patient.id,
            'count': 1,
            'hospital_number': u'0',
            'date_of_birth': self.DATE_OF_BIRTH,
            'name': u'Sally Stevens',
            'end_date': self.DATE_OF_EPISODE,
            'start_date': self.DATE_OF_EPISODE,
            'episode_id': 1,
            'categories': [u'inpatient']
        }]
        self.assertEqual(expected, summaries)
