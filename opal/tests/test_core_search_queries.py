"""
unittests for opal.core.search.queries
"""
from mock import patch
import reversion
from django.db import transaction
from opal.models import Patient, Team
from opal.core.test import OpalTestCase
from datetime import date

from opal.core.search import queries

from opal.tests.episodes import RestrictedEpisodeType

class DatabaseQueryTestCase(OpalTestCase):
    DATE_OF_BIRTH = date(day=27, month=1, year=1977)
    DATE_OF_EPISODE = date(day=1, month=2, year=2015)

    def setUp(self):
        self.patient = Patient.objects.create()
        self.episode = self.patient.create_episode()
        self.episode.date_of_episode = self.DATE_OF_EPISODE
        self.episode.save()
        self.demographics = self.patient.demographics_set.get()
        self.demographics.first_name = "Sally"
        self.demographics.surname = "Stevens"
        self.demographics.sex = "Female"
        self.demographics.hospital_number = "0"
        self.demographics.date_of_birth = self.DATE_OF_BIRTH
        self.demographics.save()

        self.general_team, _ = Team.objects.get_or_create(
            name='general', title='General Team')
        self.name_criteria = [
            {
                u'column': u'demographics',
                u'field': u'Surname',
                u'combine': u'and',
                u'query': u'Stevens',
                u'queryType': u'Equals'
            }
        ]

    def test_filter_restricted_only_user(self):
        self.user.profile.restricted_only   = True
        self.user.profile.save()
        self.patient.create_episode(category='Inpatient')
        query = queries.DatabaseQuery(self.user, self.name_criteria)
        self.assertEqual([], query.get_episodes())

    def test_filter_in_restricted_episode_types(self):
        self.user.profile.restricted_only   = True
        self.user.profile.save()
        episode2 = self.patient.create_episode(category='Restricted')
        self.assertEqual('Restricted', episode2.category)

        query = queries.DatabaseQuery(self.user, self.name_criteria)
        self.assertEqual([episode2], query.get_episodes())

    def test_get_old_episode(self):
        # episode's with old tags that have subsequently been removed
        # should still be qiried

        team_query = [dict(
            column="tagging",
            field='other_team',
            combine='and',
            query=None,
            lookup_list=[],
            queryType=None
        )]


        with transaction.atomic(), reversion.create_revision():
            other_episode = self.patient.create_episode()
            other_episode.set_tag_names(['other_team'], self.user)
            query = queries.DatabaseQuery(self.user, team_query)

        self.assertEqual([other_episode], query.get_episodes())

        with transaction.atomic(), reversion.create_revision():
            other_episode.set_tag_names([], self.user)

        self.assertEqual([other_episode], query.get_episodes())

    def test_get_episodes(self):
        query = queries.DatabaseQuery(self.user, self.name_criteria)
        self.assertEqual([self.episode], query.get_episodes())

    def test_get_episodes_searching_ft_or_fk_field(self):
        criteria = [
            {
                u'column': u'demographics',
                u'field': u'Sex',
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
            'first_name': u'Sally',
            'surname': u'Stevens',
            'end': self.DATE_OF_EPISODE,
            'start': self.DATE_OF_EPISODE,
            'patient_id': 1,
            'categories': [u'Inpatient']
        }]
        self.assertEqual(expected, summaries)
