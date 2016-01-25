from mock import MagicMock
from opal.core.patient_lists import PatientList, TaggedPatientList
from opal.tests import models
from opal.models import Patient, Team
from opal.core.test import OpalTestCase


class TaggingTestPatientList(TaggedPatientList):
    tag = "eater"
    subtag = "herbivore"

    schema = [
        models.Demographics,
    ]

class TaggingTestNotSubTag(TaggedPatientList):
    tag = "carnivore"

    schema = [
        models.Demographics,
    ]


class TestPatientList(OpalTestCase):
    def setUp(self):
        self.patient = Patient.objects.create()
        self.episode_1 = self.patient.create_episode()
        self.episode_2 = self.patient.create_episode()

    def test_tagging_set_with_subtag(self):
        ''' given an episode with certain tags and the required request we should
            only return episodes with those tags
        '''
        eater = Team.objects.create(name="eater")
        Team.objects.create(name="herbivore", parent=eater)
        self.episode_2.set_tag_names(["eater", "herbivore"], self.user)
        mock_request = MagicMock(name='Mock request')
        mock_request.user = self.user

        patient_list = PatientList.get_class(
            mock_request, tag="eater", subtag="herbivore"
        )
        self.assertEqual(
            [self.episode_2], [i for i in patient_list.get_queryset()]
        )
        serialized = patient_list.get_serialised()
        self.assertEqual(len(serialized), 1)
        self.assertEqual(serialized[0]["id"], 2)
        self.assertEqual("#/list/eater/herbivore", patient_list.url)

    def test_tagging_set_without_subtag(self):
        ''' given an episode with certain tags and the required request we should
            only return episodes with those tags
        '''
        Team.objects.create(name="carnivore")
        self.episode_2.set_tag_names(["carnivore"], self.user)
        mock_request = MagicMock(name='Mock request')
        mock_request.user = self.user

        patient_list = PatientList.get_class(
            mock_request, tag="carnivore"
        )
        self.assertEqual(
            [self.episode_2], [i for i in patient_list.get_queryset()]
        )
        serialized = patient_list.get_serialised()
        self.assertEqual(len(serialized), 1)
        self.assertEqual(serialized[0]["id"], 2)
        self.assertEqual("#/list/carnivore", patient_list.url)
