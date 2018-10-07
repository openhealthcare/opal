"""
Unittests for opal.managers
"""
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
import mock

from opal.models import Synonym
from opal.core.test import OpalTestCase
from opal.models import Patient, Episode
from opal.tests import models as test_models
from opal.managers import prefetch


class PrefetchTestCase(OpalTestCase):
    def test_prefech_fk_or_ft(self):
        _, episode_1 = self.new_patient_and_episode_please()
        _, episode_2 = self.new_patient_and_episode_please()
        test_models.Dog.objects.create(
            name="Fido"
        )
        test_models.Dog.objects.create(
            name="Spot"
        )
        hound_owner_1 = test_models.HoundOwner.objects.create(
            episode=episode_1
        )
        hound_owner_1.dog = "Fido"
        hound_owner_1.save()
        hound_owner_2 = test_models.HoundOwner.objects.create(
            episode=episode_2
        )
        hound_owner_2.dog = "Spot"
        hound_owner_2.save()
        qs = test_models.HoundOwner.objects.all()

        # testing without prefetch
        with self.assertNumQueries(4):
            self.assertEqual(qs[0].dog, "Fido")
            self.assertEqual(qs[1].dog, "Spot")

        # testign with prefetch
        with self.assertNumQueries(2):
            qs = prefetch(qs)
            self.assertEqual(qs[0].dog, "Fido")
            self.assertEqual(qs[1].dog, "Spot")

    def test_many_to_many(self):
        bowler = test_models.Hat.objects.create(name="Bowler")
        _, episode_1 = self.new_patient_and_episode_please()
        _, episode_2 = self.new_patient_and_episode_please()
        hat_wearer_1 = test_models.HatWearer.objects.create(
            episode=episode_1
        )
        hat_wearer_1.hats.add(bowler)

        hat_wearer_2 = test_models.HatWearer.objects.create(
            episode=episode_2
        )
        hat_wearer_2.hats.add(bowler)

        qs = test_models.HatWearer.objects.all()

        # testing without prefetch
        with self.assertNumQueries(3):
            for i in qs:
                for hat in i.hats.all():
                    self.assertEqual(hat.name, "Bowler")

        with self.assertNumQueries(2):
            qs = prefetch(qs)
            for i in qs:
                for hat in i.hats.all():
                    self.assertEqual(hat.name, "Bowler")


class PatientManagerTestCase(OpalTestCase):
    def setUp(self):
        self.patient_1 = Patient.objects.create()
        demographics1 = self.patient_1.demographics()
        demographics1.first_name="je ne"
        demographics1.surname="regrette"
        demographics1.hospital_number="rien"
        demographics1.save()

        self.patient_2 = Patient.objects.create()
        demographics2 = self.patient_2.demographics()
        demographics2.first_name="je joue"
        demographics2.surname="au",
        demographics2.hospital_number="football"
        demographics2.save()

    def test_hospital_number(self):
        """
        should find by hospital_number
        """
        query = Patient.objects.search('rien')
        self.assertEqual(query.get(), self.patient_1)

    def test_first_name(self):
        """
        should find by first_name
        """
        query = Patient.objects.search('je ne')
        self.assertEqual(query.get(), self.patient_1)

    def test_surname(self):
        """
        should find by last_name
        """
        query = Patient.objects.search('regrette')
        self.assertEqual(query.get(), self.patient_1)

    def test_multiple_results(self):
        """
        with multiple fields of the same name
        we only want to return one episode
        """
        query = Patient.objects.search('je')
        self.assertEqual(
            query.get(id=self.patient_1.id), self.patient_1
        )
        self.assertEqual(
            query.get(id=self.patient_2.id), self.patient_2
        )

    def test_combination(self):
        """
        should find one result from multiple
        fields
        """
        query = Patient.objects.search('je rien')
        self.assertEqual(query.get(), self.patient_1)


class EpisodeManagerTestCase(OpalTestCase):

    def setUp(self):
        self.patient = Patient.objects.create()
        self.episode = self.patient.create_episode()

        # make sure many to many serialisation goes as epected
        top = test_models.Hat.objects.create(name="top")
        hw = test_models.HatWearer.objects.create(episode=self.episode)
        hw.hats.add(top)

        # make sure free text or foreign key serialisation goes as expected
        # for actual foriegn keys
        test_models.Dog.objects.create(name="Jemima")
        do = test_models.DogOwner.objects.create(episode=self.episode)
        do.dog = "Jemima"
        do.save()

        # make sure it goes as expected for strings
        test_models.DogOwner.objects.create(episode=self.episode, dog="Philip")

    def test_search_returns_both_episodes(self):
        self.patient_1, self.episode_1_1 = self.new_patient_and_episode_please()
        self.episode_1_2 = self.patient_1.create_episode()
        demographics1 = self.patient_1.demographics()
        demographics1.first_name="je ne"
        demographics1.surname="regrette"
        demographics1.hospital_number="rien"
        demographics1.save()

        self.patient_2, self.episode_2_1 = self.new_patient_and_episode_please()
        demographics2 = self.patient_2.demographics()
        demographics2.first_name="je joue"
        demographics2.surname="au"
        demographics2.hospital_number="football"
        demographics2.save()

        episodes = Episode.objects.search("je ne")
        expected = set([self.episode_1_1.id, self.episode_1_2.id])
        found = set(episodes.values_list("id", flat=True))
        self.assertEqual(expected, found)

    def test_serialised_fields(self):
        as_dict = Episode.objects.serialised(self.user, [self.episode])[0]
        expected = [
            'id', 'category_name', 'active', 'start', 'end',
            'consistency_token', 'stage'
        ]

        for field in expected:
            self.assertIn(field, as_dict)

        dogs = set(i["dog"] for i in as_dict["dog_owner"])

        self.assertEqual(dogs, {"Jemima", "Philip"})
        self.assertEqual(as_dict["hat_wearer"][0]["hats"], ["top"])

    def test_serialised_equals_to_dict(self):
        """ Serialised is an optimisation
        """
        as_dict = Episode.objects.serialised(
            self.user, [self.episode]
        )

        expected = self.episode.to_dict(self.user)

        self.assertEqual(as_dict[0], expected)

    def test_serialised_mine_tag_other_user(self):
        tags = list(self.episode.get_tag_names(user=self.user))
        tags += ['mine']
        user2 = self.make_user('the password', username='user2')
        self.episode.set_tag_names(tags, user2)
        as_dict = Episode.objects.serialised(
            self.user, [self.episode]
        )
        self.assertEqual(as_dict[0]['tagging'][0], {'id': self.episode.id})


class LookupListQuerysetTestCase(OpalTestCase):
    def setUp(self, *args, **kwargs):
        super(LookupListQuerysetTestCase, self).setUp(*args, **kwargs)
        self.hat = self.create_model_and_synonym("Top Hat", "High Hat")

    def create_synonym(self, instance, synonym):
        ct = ContentType.objects.get_for_model(test_models.Hat)
        return Synonym.objects.create(
            name=synonym,
            object_id=instance.id,
            content_type=ct
        )

    def create_instance(self, name):
        return test_models.Hat.objects.create(name=name)

    def create_model_and_synonym(self, name, *synonyms):
        instance = self.create_instance(name)
        for synonym in synonyms:
            self.create_synonym(instance, synonym)
        return instance

    def test_get_content_type(self):
        ct = ContentType.objects.get_for_model(test_models.Hat)
        self.assertEqual(
            ct, test_models.Hat.objects.get_content_type()
        )

    def test_find_ids_from_synonyms(self):
        ids = test_models.Hat.objects.find_ids_from_synonyms(
            ["high hat"]
        )
        self.assertEqual(len(ids), 1)
        self.assertEqual(
            self.hat.id, ids[0]
        )

        ids = test_models.Hat.objects.find_ids_from_synonyms(
            ["tree"]
        )
        self.assertEqual(len(ids), 0)

    def test_find_ids_from_synonyms_case_sensive(self):
        ids = test_models.Hat.objects.find_ids_from_synonyms(
            ["High Hat"], case_sensitive=True
        )
        self.assertEqual(len(ids), 1)
        self.assertEqual(
            self.hat.id, ids[0]
        )

        ids = test_models.Hat.objects.find_ids_from_synonyms(
            ["high hat"], case_sensitive=True
        )
        self.assertEqual(len(ids), 0)

    def test_find_ids_from_synonyms_contains(self):
        ids = test_models.Hat.objects.find_ids_from_synonyms(
            ["igh"], contains=True
        )
        self.assertEqual(len(ids), 1)
        self.assertEqual(
            self.hat.id, ids[0]
        )

        ids = test_models.Hat.objects.find_ids_from_synonyms(
            ["figh"], contains=True
        )
        self.assertEqual(len(ids), 0)

    def test_find_ids_from_synonyms_case_sensitive_and_contains(self):
        # sqlite does not support case insensitive LIKE clauses
        if settings.DATABASES["default"]["ENGINE"].endswith("sqlite3"):
            return

        ids = test_models.Hat.objects.find_ids_from_synonyms(
            ["igh"], contains=True, case_sensitive=True
        )
        self.assertEqual(len(ids), 1)
        self.assertEqual(
            self.hat.id, ids[0]
        )

        ids = test_models.Hat.objects.find_ids_from_synonyms(
            ["Igh"], contains=True, case_sensitive=True
        )
        self.assertEqual(len(ids), 0)

    def test_find_ids_from_synonyms_distinct(self):
        bowler = self.create_model_and_synonym(
            "Bowler", "Bob Hat", "Bob Cap"
        )
        ids = test_models.Hat.objects.find_ids_from_synonyms(
            ["Bob"], contains=True
        )
        self.assertEqual(len(ids), 1)
        self.assertEqual(ids[0], bowler.id)

    def test_get_query_arg_standard(self):
        query_arg = test_models.Hat.objects.get_query_arg(
            contains=False, case_sensitive=False
        )
        self.assertEqual(
            query_arg, "name__iexact"
        )

    def test_get_query_arg_contains(self):
        query_arg = test_models.Hat.objects.get_query_arg(
            contains=True, case_sensitive=False
        )
        self.assertEqual(
            query_arg, "name__icontains"
        )

    def test_get_query_arg_case_sensitive(self):
        query_arg = test_models.Hat.objects.get_query_arg(
            contains=False, case_sensitive=True
        )
        self.assertEqual(
            query_arg, "name"
        )

    def test_get_query_arg_case_sensitive_and_contains(self):
        query_arg = test_models.Hat.objects.get_query_arg(
            case_sensitive=True, contains=True
        )
        self.assertEqual(
            query_arg, "name__contains"
        )

    def test_search(self):
        with mock.patch("opal.managers.LookupListQueryset.search_many") as s:
            test_models.Hat.objects.search("hello")
        s.assert_called_once_with(
            ["hello"], contains=False, case_sensitive=False
        )

        with mock.patch("opal.managers.LookupListQueryset.search_many") as s:
            test_models.Hat.objects.search("hello", contains=True)
        s.assert_called_once_with(
            ["hello"], contains=True, case_sensitive=False
        )

        with mock.patch("opal.managers.LookupListQueryset.search_many") as s:
            test_models.Hat.objects.search("hello", case_sensitive=True)
        s.assert_called_once_with(
            ["hello"], contains=False, case_sensitive=True
        )

    def test_search_many(self):
        bowler = self.create_model_and_synonym(
            "Bowler", "Bob Hat", "Bob Cap"
        )
        self.create_model_and_synonym(
            "other", "unused"
        )
        hats = test_models.Hat.objects.search_many(["bob hat", "top hat"])
        self.assertTrue(
            hats.filter(id=bowler.id).exists()
        )
        self.assertTrue(
            hats.filter(id=self.hat.id).exists()
        )
        self.assertTrue(
            hats.count(), 2
        )

    def test_search_many_case_sensitive_name(self):
        bowler = self.create_model_and_synonym(
            "Bowler", "Bob Hat", "Bob Cap"
        )
        self.create_model_and_synonym(
            "other", "unused"
        )
        hats = test_models.Hat.objects.search_many(
            ["Bob Hat", "Top Hat"], case_sensitive=True
        )
        self.assertTrue(
            hats.filter(id=bowler.id).exists()
        )
        self.assertTrue(
            hats.filter(id=self.hat.id).exists()
        )
        self.assertTrue(
            hats.count(), 2
        )
        if settings.DATABASES["default"]["ENGINE"].endswith("sqlite3"):
            return

        hats = test_models.Hat.objects.search_many(
            ["bob hat", "top hat"], case_sensitive=False
        )
        self.assertTrue(hats.exists())

        hats = test_models.Hat.objects.search_many(
            ["bob hat", "top hat"], case_sensitive=True
        )
        self.assertFalse(hats.exists())

    def test_search_many_contains_name(self):
        bowler = self.create_model_and_synonym(
            "Bowler", "Bob Hat", "Bob Cap"
        )
        self.create_model_and_synonym(
            "other", "unused"
        )
        hats = test_models.Hat.objects.search_many(
            ["hat", "cap"], contains=True
        )
        self.assertTrue(
            hats.filter(id=bowler.id).exists()
        )
        self.assertTrue(
            hats.filter(id=self.hat.id).exists()
        )
        self.assertTrue(
            hats.count(), 2
        )

    def test_multiple_search_missing_results(self):
        result = test_models.Hat.objects.search_many(["High Hat", "Bob Cap"])
        self.assertEqual(result.get(), self.hat)
