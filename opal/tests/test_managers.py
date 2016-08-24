"""
Unittests for opal.managers
"""
from opal.core.test import OpalTestCase
from opal.models import Patient, Episode
from opal.tests.models import Hat, HatWearer, Dog, DogOwner

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
        top = Hat.objects.create(name="top")
        hw = HatWearer.objects.create(episode=self.episode)
        hw.hats.add(top)

        # make sure free text or foreign key serialisation goes as expected
        # for actual foriegn keys
        Dog.objects.create(name="Jemima")
        do = DogOwner.objects.create(episode=self.episode)
        do.dog = "Jemima"
        do.save()

        # make sure it goes as expected for strings
        DogOwner.objects.create(episode=self.episode, dog="Philip")

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
            'id', 'category_name', 'active', 'date_of_admission', 'discharge_date',
            'consistency_token', 'date_of_episode', 'stage'
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
