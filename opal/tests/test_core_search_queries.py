"""
unittests for opal.core.search.queries
"""
from datetime import date

from django.db import transaction
import reversion

from opal.models import Episode, Patient, Team
from opal.core.test import OpalTestCase
from opal.tests.episodes import RestrictedEpisodeCategory

from opal.core.search import queries

from opal.tests import models as testmodels

class PatientSummaryTestCase(OpalTestCase):

    def test_update_sets_start(self):
        patient, episode = self.new_patient_and_episode_please()
        summary = queries.PatientSummary(episode)
        self.assertEqual(None, summary.start)
        the_date = date(day=27, month=1, year=1972)
        episode2 = patient.create_episode(date_of_admission=the_date)
        summary.update(episode2)
        self.assertEqual(summary.start, the_date)

    def test_update_sets_end(self):
        patient, episode = self.new_patient_and_episode_please()
        summary = queries.PatientSummary(episode)
        self.assertEqual(None, summary.start)
        the_date = date(day=27, month=1, year=1972)
        episode2 = patient.create_episode(discharge_date=the_date)
        summary.update(episode2)
        self.assertEqual(summary.end, the_date)

class QueryBackendTestCase(OpalTestCase):

    def test_fuzzy_query(self):
        with self.assertRaises(NotImplementedError):
            queries.QueryBackend(self.user, 'aquery').fuzzy_query()

    def test_get_episodes(self):
        with self.assertRaises(NotImplementedError):
            queries.QueryBackend(self.user, 'aquery').get_episodes()

    def test_description(self):
        with self.assertRaises(NotImplementedError):
            queries.QueryBackend(self.user, 'aquery').description()

    def test_get_patients(self):
        with self.assertRaises(NotImplementedError):
            queries.QueryBackend(self.user, 'aquery').get_patients()

    def test_get_patient_summaries(self):
        with self.assertRaises(NotImplementedError):
            queries.QueryBackend(self.user, 'aquery').get_patient_summaries()


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

    def test_episodes_for_boolean_fields(self):
        criteria = dict(
            column='demographics', field='Death Indicator',
            combine='and', query='false', queryType='Equals'
        )
        query = queries.DatabaseQuery(self.user, [criteria])
        self.assertEqual([self.episode], query.get_episodes())

    def test_episodes_for_boolean_fields_episode_subrecord(self):
        criteria = dict(
            column='hat_wearer', field='Wearing A Hat',
            combine='and', query='true', queryType='Equals'
        )
        hatwearer = testmodels.HatWearer(episode=self.episode, wearing_a_hat=True)
        hatwearer.save()
        query = queries.DatabaseQuery(self.user, [criteria])
        self.assertEqual([self.episode], query.get_episodes())

    def test_episodes_for_date_fields(self):
        criteria = dict(
            column='dog_owner', field='Ownership Start Date',
            combine='and', query='1/12/1999', queryType='Equals'
        )
        dogowner = testmodels.DogOwner(
            episode=self.episode, ownership_start_date=date(1999, 12, 1))
        dogowner.save()
        query = queries.DatabaseQuery(self.user, [criteria])
        self.assertEqual([self.episode], query.get_episodes())

    def test_episodes_for_date_fields_patient_subrecord(self):
        criteria = dict(
            column='birthday', field='Birth Date',
            combine='and', query='1/12/1999', queryType='Equals'
        )
        birthday = testmodels.Birthday(
            patient=self.patient, birth_date=date(1999, 12, 1))
        birthday.save()
        query = queries.DatabaseQuery(self.user, [criteria])
        self.assertEqual([self.episode], query.get_episodes())

    def test_episodes_for_date_fields_before(self):
        criteria = dict(
            column='dog_owner', field='Ownership Start Date',
            combine='and', query='1/12/2000', queryType='Before'
        )
        dogowner = testmodels.DogOwner(
            episode=self.episode, ownership_start_date=date(1999, 12, 1))
        dogowner.save()
        query = queries.DatabaseQuery(self.user, [criteria])
        self.assertEqual([self.episode], query.get_episodes())

    def test_episodes_for_date_fields_after(self):
        criteria = dict(
            column='dog_owner', field='Ownership Start Date',
            combine='and', query='1/12/1998', queryType='After'
        )
        dogowner = testmodels.DogOwner(
            episode=self.episode, ownership_start_date=date(1999, 12, 1))
        dogowner.save()
        query = queries.DatabaseQuery(self.user, [criteria])
        self.assertEqual([self.episode], query.get_episodes())

    def test_episodes_for_m2m_fields(self):
        criteria = dict(
            column='hat_wearer', field='Hats',
            combine='and', query='Bowler', queryType='Equals'
        )

        bowler = testmodels.Hat(name='Bowler')
        bowler.save()

        hatwearer = testmodels.HatWearer(episode=self.episode)
        hatwearer.save()
        hatwearer.hats.add(bowler)
        hatwearer.save()

        query = queries.DatabaseQuery(self.user, [criteria])
        self.assertEqual([self.episode], query.get_episodes())

    def test_episodes_for_m2m_fields_patient_subrecord(self):
        criteria = dict(
            column='favourite_dogs', field='Dogs',
            combine='and', query='Dalmation', queryType='Equals'
        )

        dalmation = testmodels.Dog(name='Dalmation')
        dalmation.save()

        favouritedogs = testmodels.FavouriteDogs(patient=self.patient)
        favouritedogs.save()

        favouritedogs.dogs.add(dalmation)
        favouritedogs.save()
        query = queries.DatabaseQuery(self.user, [criteria])
        self.assertEqual([self.episode], query.get_episodes())


    def test_filter_restricted_only_user(self):
        self.user.profile.restricted_only   = True
        self.user.profile.save()
        self.patient.create_episode(category='Inpatient')
        query = queries.DatabaseQuery(self.user, self.name_criteria)
        self.assertEqual([], query.get_episodes())

    def test_filter_in_restricted_episode_types(self):
        self.user.profile.restricted_only   = True
        self.user.profile.save()
        episode2 = self.patient.create_episode(category_name='Restricted')
        self.assertEqual('Restricted', episode2.category_name)

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

    def test_update_patient_summaries(self):
        """ with a patient with multiple episodes
            we expect it to aggregate these into summaries
        """
        start_date = date(day=1, month=2, year=2014)
        episode_2 = self.patient.create_episode(
            date_of_episode=start_date
        )
        end_date = date(day=1, month=2, year=2016)
        episode_3 = self.patient.create_episode(
            date_of_episode=end_date
        )
        query = queries.DatabaseQuery(self.user, self.name_criteria)
        summaries = query.get_patient_summaries()
        expected = [{
            'id': self.patient.id,
            'count': 3,
            'hospital_number': u'0',
            'date_of_birth': self.DATE_OF_BIRTH,
            'first_name': u'Sally',
            'surname': u'Stevens',
            'end': end_date,
            'start': start_date,
            'patient_id': 1,
            'categories': [u'Inpatient']
        }]
        self.assertEqual(expected, summaries)
