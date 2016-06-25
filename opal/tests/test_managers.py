from opal.core.test import OpalTestCase
from opal.models import Patient, Episode


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

    def test_returns_both_episodes(self):
        episodes = Episode.objects.search("je ne")
        expected = set([self.episode_1_1.id, self.episode_1_2.id])
        found = set(episodes.values_list("id", flat=True))
        self.assertEqual(expected, found)
