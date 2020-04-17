"""
Unittests for opal.core.search.queries
"""
from datetime import date

from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from unittest.mock import patch, MagicMock
from reversion import revisions as reversion
from opal.tests.episodes import RestrictedEpisodeCategory

from opal.core.search.search_rule import SearchRule
from opal.models import Synonym, Gender

from opal.core.test import OpalTestCase

from opal.core.search import queries

from opal.tests import models as testmodels


# don't remove this, we use it to discover the restricted episode category
from opal.tests.episodes import RestrictedEpisodeCategory  # NOQA


class PatientSummaryTestCase(OpalTestCase):

    def test_update_sets_start(self):
        patient, episode = self.new_patient_and_episode_please()
        summary = queries.PatientSummary(episode)
        self.assertEqual(None, summary.start)
        the_date = date(day=27, month=1, year=1972)
        episode2 = patient.create_episode(start=the_date)
        summary.update(episode2)
        self.assertEqual(summary.start, the_date)

    def test_update_sets_end(self):
        patient, episode = self.new_patient_and_episode_please()
        summary = queries.PatientSummary(episode)
        self.assertEqual(None, summary.start)
        the_date = date(day=27, month=1, year=1972)
        episode2 = patient.create_episode(end=the_date)
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
        self.patient, self.episode = self.new_patient_and_episode_please()
        self.episode.date_of_episode = self.DATE_OF_EPISODE
        self.episode.start = self.DATE_OF_EPISODE
        self.episode.end = self.DATE_OF_EPISODE
        self.episode.save()
        self.demographics = self.patient.demographics()
        self.demographics.first_name = "Sally"
        self.demographics.surname = "Stevens"
        self.demographics.sex = "Female"
        self.demographics.hospital_number = "0"
        self.demographics.date_of_birth = self.DATE_OF_BIRTH
        self.demographics.save()

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

    def test_episodes_for_number_fields_greater_than(self):
        testmodels.FavouriteNumber.objects.create(
            patient=self.patient, number=10
        )
        criteria = dict(
            column='favourite_number',
            field='number',
            combine='and',
            query=1,
            queryType='Greater Than'
        )
        query = queries.DatabaseQuery(self.user, [criteria])
        self.assertEqual([self.episode], query.get_episodes())

        criteria["query"] = 100
        query = queries.DatabaseQuery(self.user, [criteria])
        self.assertEqual([], query.get_episodes())

    def test_episodes_for_number_fields_less_than(self):
        testmodels.FavouriteNumber.objects.create(
            patient=self.patient, number=10
        )
        criteria = dict(
            column='favourite_number',
            field='number',
            combine='and',
            query=11,
            queryType='Less Than'
        )
        query = queries.DatabaseQuery(self.user, [criteria])
        self.assertEqual([self.episode], query.get_episodes())

        criteria["query"] = 1
        query = queries.DatabaseQuery(self.user, [criteria])
        self.assertEqual([], query.get_episodes())

    def test_episodes_for_boolean_fields_episode_subrecord(self):
        criteria = dict(
            column='hat_wearer', field='Wearing A Hat',
            combine='and', query='true', queryType='Equals'
        )
        hatwearer = testmodels.HatWearer(
            episode=self.episode, wearing_a_hat=True
        )
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

    def test_episodes_for_m2m_fields_equals_with_synonyms(self):
        criteria = dict(
            column='hat_wearer', field='Hats',
            combine='and', query='Derby', queryType='Equals'
        )

        bowler = testmodels.Hat.objects.create(name='Bowler')
        content_type = ContentType.objects.get_for_model(testmodels.Hat)
        Synonym.objects.get_or_create(
            content_type=content_type,
            object_id=bowler.id,
            name="Derby"
        )

        hatwearer = testmodels.HatWearer(episode=self.episode)
        hatwearer.save()
        hatwearer.hats.add(bowler)
        hatwearer.save()

        query = queries.DatabaseQuery(self.user, [criteria])
        self.assertEqual([self.episode], query.get_episodes())

    def test_episodes_for_m2m_fields_contains_synonym_and_name(self):
        criteria = dict(
            column='hat_wearer', field='Hats',
            combine='and', query='Der', queryType='Contains'
        )

        bowler = testmodels.Hat.objects.create(name='Bowler')
        content_type = ContentType.objects.get_for_model(testmodels.Hat)
        Synonym.objects.get_or_create(
            content_type=content_type,
            object_id=bowler.id,
            name="Derby"
        )

        hatwearer = testmodels.HatWearer(episode=self.episode)
        hatwearer.save()
        hatwearer.hats.add(bowler)
        hatwearer.save()

        # now we add another episode with an actual hat
        derbishire = testmodels.Hat.objects.create(name='derbishire')
        _, other_episode = self.new_patient_and_episode_please()

        hatwearer = testmodels.HatWearer(episode=other_episode)
        hatwearer.save()
        hatwearer.hats.add(derbishire)
        hatwearer.save()

        query = queries.DatabaseQuery(self.user, [criteria])
        expected = set([self.episode.id, other_episode.id])
        found = set([i.id for i in query.get_episodes()])
        self.assertEqual(expected, found)

    def test_fuzzy_query(self):
        """ It should return the patients that
            match the criteria ordered in by
            their related episode id descending
        """
        patient_1, episode_1 = self.new_patient_and_episode_please()
        patient_2, episode_2 = self.new_patient_and_episode_please()
        patient_3, episode_3 = self.new_patient_and_episode_please()
        testmodels.Demographics.objects.filter(
            patient__in=[patient_1, patient_2, patient_3]
        ).update(
            first_name="tree"
        )
        patient_2.create_episode()
        # this patient, episode should not be found
        self.new_patient_and_episode_please()
        query = queries.DatabaseQuery(self.user, "tree")
        patients = query.fuzzy_query()

        # expectation is that patient 2 comes last as
        # they have the most recent episode
        self.assertEqual(
            list(patients),
            [patient_2, patient_3, patient_1]
        )

    def test_distinct_episodes_for_m2m_fields_containing_synonsyms_and_names(
        self
    ):
        criteria = dict(
            column='hat_wearer', field='Hats',
            combine='and', query='Der', queryType='Contains'
        )

        bowler = testmodels.Hat.objects.create(name='Bowler')
        content_type = ContentType.objects.get_for_model(testmodels.Hat)
        Synonym.objects.get_or_create(
            content_type=content_type,
            object_id=bowler.id,
            name="Derby"
        )

        hatwearer = testmodels.HatWearer(episode=self.episode)
        hatwearer.save()
        hatwearer.hats.add(bowler)
        hatwearer.save()

        derbishire = testmodels.Hat.objects.create(name='derbishire')
        hatwearer.hats.add(derbishire)
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

        favouritedogs = testmodels.FavouriteDogs.objects.create(
            patient=self.patient
        )

        favouritedogs.dogs.add(dalmation)
        query = queries.DatabaseQuery(self.user, [criteria])
        self.assertEqual([self.episode], query.get_episodes())

    def test_episodes_for_fkorft_fields_for_patient_subrecord(self):
        criteria = dict(
            column='demographics', field='sex',
            combine='and', query='Unknown', queryType='Equals'
        )
        unknown = Gender(name='Unknown')
        unknown.save()
        demographics = self.patient.demographics()
        demographics.sex = 'Unknown'
        demographics.save()
        query = queries.DatabaseQuery(self.user, [criteria])
        self.assertEqual([self.episode], query.get_episodes())

    def test_episodes_for_fkorft_fields_for_patient_subrecord_with_multiple_episodes(self):
        criteria = dict(
            column='demographics', field='sex',
            combine='and', query='Unknown', queryType='Equals'
        )
        unknown = Gender(name='Unknown')
        unknown.save()
        demographics = self.patient.demographics()
        demographics.sex = 'Unknown'
        demographics.save()
        query = queries.DatabaseQuery(self.user, [criteria])
        self.assertEqual([self.episode], query.get_episodes())

    def test_episodes_for_fkorft_fields_exact_episode_subrecord(self):
        criteria = dict(
            column='hound_owner', field='dog',
            combine='and', query='Dalmation', queryType='Equals'
        )

        dalmation = testmodels.Dog(name='Dalmation')
        dalmation.save()

        hound_owner = testmodels.HoundOwner.objects.create(
            episode=self.episode
        )
        hound_owner.dog = "Dalmation"
        hound_owner.save()
        query = queries.DatabaseQuery(self.user, [criteria])
        self.assertEqual([self.episode], query.get_episodes())

    def test_episode_for_exact_fkorft_synonym(self):
        criteria = dict(
            column='hound_owner', field='dog',
            combine='and', query='Dalmation', queryType='Equals'
        )

        spotted_dog = testmodels.Hat.objects.create(name='Spotted Dog')
        content_type = ContentType.objects.get_for_model(testmodels.Hat)
        Synonym.objects.get_or_create(
            content_type=content_type,
            object_id=spotted_dog.id,
            name="Dalmation"
        )

        hound_owner = testmodels.HoundOwner.objects.create(
            episode=self.episode
        )
        hound_owner.dog = "Dalmation"
        hound_owner.save()
        query = queries.DatabaseQuery(self.user, [criteria])
        self.assertEqual([self.episode], query.get_episodes())

    def test_episode_for_exact_fkorft_free_text(self):
        criteria = dict(
            column='hound_owner', field='dog',
            combine='and', query='dalmation', queryType='Equals'
        )

        hound_owner = testmodels.HoundOwner.objects.create(
            episode=self.episode
        )
        hound_owner.dog = "Dalmation"
        hound_owner.save()
        query = queries.DatabaseQuery(self.user, [criteria])
        self.assertEqual([self.episode], query.get_episodes())

    def test_episode_for_fkorft_fields_contains_episode_subrecord(self):
        criteria = dict(
            column='hound_owner', field='dog',
            combine='and', query='dal', queryType='Contains'
        )

        dalmation = testmodels.Dog(name='Dalmation')
        dalmation.save()

        hound_owner = testmodels.HoundOwner.objects.create(
            episode=self.episode
        )
        hound_owner.dog = "Dalmation"
        hound_owner.save()
        query = queries.DatabaseQuery(self.user, [criteria])
        self.assertEqual([self.episode], query.get_episodes())

    def test_episode_fkorft_for_contains_synonym(self):
        criteria = dict(
            column='hound_owner', field='dog',
            combine='and', query='dal', queryType='Contains'
        )

        spotted_dog = testmodels.Dog.objects.create(name='Spotted Dog')
        content_type = ContentType.objects.get_for_model(testmodels.Dog)
        Synonym.objects.get_or_create(
            content_type=content_type,
            object_id=spotted_dog.id,
            name="Dalmation"
        )

        hound_owner = testmodels.HoundOwner.objects.create(
            episode=self.episode
        )
        hound_owner.dog = "Dalmation"
        hound_owner.save()
        query = queries.DatabaseQuery(self.user, [criteria])
        self.assertEqual([self.episode], query.get_episodes())

    def test_episode_fkorft_for_contains_ft(self):
        criteria = dict(
            column='hound_owner', field='dog',
            combine='and', query='dal', queryType='Contains'
        )

        hound_owner = testmodels.HoundOwner.objects.create(
            episode=self.episode
        )
        hound_owner.dog = "Dalmation"
        hound_owner.save()
        query = queries.DatabaseQuery(self.user, [criteria])
        self.assertEqual([self.episode], query.get_episodes())

    def test_episode_fkorft_for_contains_synonym_name_and_ft(self):
        criteria = dict(
            column='hound_owner', field='dog',
            combine='and', query='dal', queryType='Contains'
        )

        spotted_dog = testmodels.Dog.objects.create(name='Spotted Dog')
        content_type = ContentType.objects.get_for_model(testmodels.Dog)
        Synonym.objects.get_or_create(
            content_type=content_type,
            object_id=spotted_dog.id,
            name="Dalmation"
        )

        hound_owner = testmodels.HoundOwner.objects.create(
            episode=self.episode
        )
        hound_owner.dog = "Dalmation"
        hound_owner.save()

        _, episode_2 = self.new_patient_and_episode_please()
        hound_owner = testmodels.HoundOwner.objects.create(
            episode=episode_2
        )
        hound_owner.dog = "Dalwinion"
        hound_owner.save()
        query = queries.DatabaseQuery(self.user, [criteria])
        self.assertEqual([self.episode, episode_2], query.get_episodes())

    def test_episode_fkorft_contains_distinct(self):
        criteria = dict(
            column='hound_owner', field='dog',
            combine='and', query='dal', queryType='Contains'
        )

        spotted_dog = testmodels.Dog.objects.create(name='Spotted Dog')
        content_type = ContentType.objects.get_for_model(testmodels.Dog)
        Synonym.objects.get_or_create(
            content_type=content_type,
            object_id=spotted_dog.id,
            name="Dalmation"
        )

        hound_owner = testmodels.HoundOwner.objects.create(
            episode=self.episode
        )
        hound_owner.dog = "Dalmation"
        hound_owner.save()
        episode_2 = self.patient.create_episode()

        hound_owner = testmodels.HoundOwner.objects.create(
            episode=episode_2
        )
        hound_owner.dog = "Dalwinion"
        hound_owner.save()
        query = queries.DatabaseQuery(self.user, [criteria])
        expected = set([self.episode.id, episode_2.id])
        found = set(i.id for i in query.get_episodes())
        self.assertEqual(expected, found)

    def test_episodes_for_criteria_episode_subrecord_string_field(self):
        criteria = [
            {
                u'column': u'hat_wearer',
                u'field': u'Name',
                u'combine': u'and',
                u'query': u'Bowler',
                u'queryType': u'Equals'
            }
        ]
        query = queries.DatabaseQuery(self.user, criteria)
        res = query.episodes_for_criteria(criteria[0])
        self.assertEqual([], list(res))

    def test_episodes_for_criteria_search_rule_used(self):
        criteria = [
            {
                u'column': u'hat_wearer',
                u'field': u'Name',
                u'combine': u'and',
                u'query': u'Bowler',
                u'queryType': u'Equals'
            }
        ]

        class HatWearerQuery(object):
            def query(self, given_query):
                pass

        with patch.object(SearchRule, "get") as search_rule_get:
            with patch.object(HatWearerQuery, "query") as hat_wearer_query:
                search_rule_get.return_value = HatWearerQuery
                query = queries.DatabaseQuery(self.user, criteria)
                query.episodes_for_criteria(criteria[0])
                search_rule_get.assert_called_once_with("hat_wearer")
                hat_wearer_query.assert_called_once_with(criteria[0])

    def test_episodes_without_restrictions_no_matches(self):
        query = queries.DatabaseQuery(self.user, self.name_criteria)
        query.query = []
        result = query._episodes_without_restrictions()
        self.assertEqual([], result)

    def test_episodes_without_restrictions(self):
        query = queries.DatabaseQuery(self.user, self.name_criteria)
        result = query._episodes_without_restrictions()
        self.assertEqual(self.episode, list(result)[0])

    def test_filter_restricted_only_user(self):
        self.user.profile.restricted_only = True
        self.user.profile.save()
        self.patient.create_episode(category_name='Inpatient')
        query = queries.DatabaseQuery(self.user, self.name_criteria)
        self.assertEqual([], query.get_episodes())

    def test_filter_in_restricted_episode_types(self):
        self.user.profile.restricted_only = True
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

    def test_gets_mine_only(self):
        # an episode tagged with 'mine' should return
        # only episodes that I have tagged with mine
        team_query = [dict(
            column="tagging",
            field='mine',
            combine='and',
            query=None,
            lookup_list=[],
            queryType=None
        )]

        other_user = User.objects.create(username="other")
        _, other_users_episode = self.new_patient_and_episode_please()

        with transaction.atomic(), reversion.create_revision():
            episode = self.patient.create_episode()
            episode.set_tag_names(['mine'], self.user)
            other_users_episode.set_tag_names(['mine'], other_user)
            query = queries.DatabaseQuery(self.user, team_query)

        self.assertEqual([episode], query.get_episodes())

        with transaction.atomic(), reversion.create_revision():
            episode.set_tag_names([], self.user)

        self.assertEqual([episode], query.get_episodes())

    def test_get_episodes(self):
        query = queries.DatabaseQuery(self.user, self.name_criteria)
        self.assertEqual([self.episode], query.get_episodes())

    def test_get_episodes_multi_query(self):
        criteria = [
            {
                u'column': u'demographics',
                u'field': u'Sex',
                u'combine': u'and',
                u'query': u'Female',
                u'queryType': u'Equals'
            },
            self.name_criteria[0]
        ]
        query = queries.DatabaseQuery(self.user, criteria)
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

    def test_episodes_searching_fk_or_ft_fields_with_synonym_values(self):
        criteria = [
            {
                u'column': u'demographics',
                u'field': u'Sex',
                u'combine': u'and',
                u'query': u'F',
                u'queryType': u'Equals'
            }
        ]
        female = Gender.objects.create(name="Female")
        ct = ContentType.objects.get_for_model(Gender)
        Synonym.objects.create(content_type=ct, name="F", object_id=female.id)
        demographics = self.patient.demographics()
        demographics.sex = "F"
        demographics.save()
        self.assertEqual("Female", demographics.sex)
        query = queries.DatabaseQuery(self.user, criteria)
        self.assertEqual([self.episode], query.get_episodes())

    def test_get_episodes_searching_episode_subrecord_ft_or_fk_fields(self):
        criteria = [
            {
                u'column': u'dog_owner',
                u'field': u'Dog',
                u'combine': u'and',
                u'query': u'Terrier',
                u'queryType': u'Equals'
            }
        ]
        dog_owner = testmodels.DogOwner.objects.create(episode=self.episode)
        dog_owner.dog = 'Terrier'
        dog_owner.save()
        query = queries.DatabaseQuery(self.user, criteria)
        self.assertEqual([self.episode], query.get_episodes())

    def test_get_patient_summaries(self):
        query = queries.DatabaseQuery(self.user, self.name_criteria)
        summaries = query.get_patient_summaries()
        expected = [{
            'count': 1,
            'hospital_number': u'0',
            'date_of_birth': self.DATE_OF_BIRTH,
            'first_name': u'Sally',
            'surname': u'Stevens',
            'end': self.DATE_OF_EPISODE,
            'start': self.DATE_OF_EPISODE,
            'patient_id': self.patient.id,
            'categories': [u'Inpatient']
        }]
        self.assertEqual(expected, summaries)

    def test_update_patient_summaries(self):
        """ with a patient with multiple episodes
            we expect it to aggregate these into summaries
        """
        start_date = date(day=1, month=2, year=2014)
        self.patient.create_episode(
            start=start_date
        )
        end_date = date(day=1, month=2, year=2016)
        self.patient.create_episode(
            end=end_date
        )
        query = queries.DatabaseQuery(self.user, self.name_criteria)
        summaries = query.get_patient_summaries()
        expected = [{
            'count': 3,
            'hospital_number': u'0',
            'date_of_birth': self.DATE_OF_BIRTH,
            'first_name': u'Sally',
            'surname': u'Stevens',
            'end': end_date,
            'start': start_date,
            'patient_id': self.patient.id,
            'categories': [u'Inpatient']
        }]
        self.assertEqual(expected, summaries)


class CreateQueryTestCase(OpalTestCase):

    @patch('opal.core.search.queries.stringport')
    def test_from_settings(self, stringport):
        mock_backend = MagicMock('Mock Backend')
        stringport.return_value = mock_backend

        with self.settings(OPAL_SEARCH_BACKEND='mybackend'):
            backend = queries.create_query(self.user, [])
            self.assertEqual(mock_backend.return_value, backend)
            mock_backend.assert_called_with(self.user, [])
