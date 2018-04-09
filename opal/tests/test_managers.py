"""
Unittests for opal.managers
"""
from opal.core.test import OpalTestCase
from opal.models import Patient, Episode
from opal.tests import models as test_models
from opal.managers import prefetch


class PatientManagerTestCase(OpalTestCase):
    def setUp(self):
        self.patient_1 = Patient.objects.create()
        self.patient_1.demographics_set.all().update(
            first_name="je ne",
            surname="regrette",
            hospital_number="rien"
        )

        self.patient_2 = Patient.objects.create()
        self.patient_2.demographics_set.all().update(
            first_name="je joue",
            surname="au",
            hospital_number="football"
        )

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
        self.patient_1.demographics_set.all().update(
            first_name="je ne",
            surname="regrette",
            hospital_number="rien"
        )

        self.patient_2, self.episode_2_1 = self.new_patient_and_episode_please()
        self.patient_2.demographics_set.all().update(
            first_name="je joue",
            surname="au",
            hospital_number="football"
        )

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
            self.user, [self.episode], episode_history=True
        )

        expected = self.episode.to_dict(self.user)

        self.assertEqual(as_dict[0], expected)

    def test_serialised_mine_tag_other_user(self):
        tags = list(self.episode.get_tag_names(user=self.user))
        tags += ['mine']
        user2 = self.make_user('the password', username='user2')
        self.episode.set_tag_names(tags, user2)
        as_dict = Episode.objects.serialised(
            self.user, [self.episode], episode_history=False
        )
        self.assertEqual(as_dict[0]['tagging'][0], {'id': 1})


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


class EpisodeSubrecordQuerysetTestCase(OpalTestCase):
    def test_for_episode(self):
        _, episode = self.new_patient_and_episode_please()
        test_models.DogOwner.objects.create(
            name="Fido", episode=episode
        )
        result = test_models.DogOwner.objects.for_episode(
            episode
        )
        self.assertEqual(result.get().name, "Fido")

    def test_for_episodes(self):
        _, episode_1 = self.new_patient_and_episode_please()
        test_models.DogOwner.objects.create(
            name="Fido", episode=episode_1
        )

        _, episode_1 = self.new_patient_and_episode_please()
        test_models.DogOwner.objects.create(
            name="Spot", episode=episode_1
        )
        # create one more to make sure we work
        # even if there are no subrecords
        self.new_patient_and_episode_please()
        result = test_models.DogOwner.objects.for_episodes(
            Episode.objects.all()
        ).order_by("name")
        self.assertEqual(result.count(), 2)
        self.assertEqual(result[0].name, "Fido")
        self.assertEqual(result[1].name, "Spot")


class PatientSubrecordQuerysetTestCase(OpalTestCase):
    def test_for_episode(self):
        patient, episode = self.new_patient_and_episode_please()
        test_models.InvisibleDog.objects.create(
            name="Fido", patient=patient
        )
        result = test_models.InvisibleDog.objects.for_episode(
            episode
        )
        self.assertEqual(result.get().name, "Fido")

    def test_for_patients(self):
        patient_1, _ = self.new_patient_and_episode_please()
        test_models.InvisibleDog.objects.create(
            name="Fido", patient=patient_1
        )

        patient_2, _ = self.new_patient_and_episode_please()
        test_models.InvisibleDog.objects.create(
            name="Spot", patient=patient_2
        )
        patient_3, _ = self.new_patient_and_episode_please()
        result = test_models.InvisibleDog.objects.for_patients(
            Patient.objects.all()
        ).order_by("name")
        self.assertEqual(result.count(), 2)
        self.assertEqual(result[0].name, "Fido")
        self.assertEqual(result[1].name, "Spot")
