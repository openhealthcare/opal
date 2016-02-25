"""
Unittests for opal.core.patient_lists
"""
from django.contrib.auth.models import User
from mock import MagicMock, PropertyMock, patch

from opal.core.patient_lists import PatientList, TaggedPatientList
from opal.tests import models
from opal.models import Patient, Team, UserProfile
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
        self.restricted_user = User.objects.create(username='restrictedonly')
        self.profile, _ = UserProfile.objects.get_or_create(
            user=self.restricted_user, restricted_only=True
        )

    def test_unimplemented_schema(self):
        with self.assertRaises(ValueError):
            schema = PatientList().schema

    def test_unimplemented_queryset(self):
        with self.assertRaises(ValueError):
            queryset = PatientList().queryset

    def test_get_queryset_default(self):
        mock_queryset = MagicMock('Mock Queryset')
        with patch.object(PatientList, 'queryset', new_callable=PropertyMock) as queryset:
            queryset.return_value = mock_queryset
            self.assertEqual(mock_queryset, PatientList().get_queryset())

    def test_visible_to(self):
        self.assertTrue(TaggingTestPatientList.visible_to(self.user))

    def test_visible_to_restricted_only(self):
        self.assertFalse(TaggingTestPatientList.visible_to(self.restricted_user))

    def test_for_user(self):
        self.assertIn(TaggingTestPatientList, list(PatientList.for_user(self.user)))
        self.assertIn(TaggingTestNotSubTag, list(PatientList.for_user(self.user)))

    def test_for_user_restricted_only(self):
        self.assertEqual([], list(PatientList.for_user(self.restricted_user)))


class TestTaggedPatientList(OpalTestCase):
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

        patient_list = PatientList.get('eater-herbivore')()
        self.assertEqual(
            [self.episode_2], [i for i in patient_list.get_queryset()]
        )
        serialized = patient_list.to_dict(self.user)
        self.assertEqual(len(serialized), 1)
        self.assertEqual(serialized[0]["id"], 2)

    def test_tagging_set_without_subtag(self):
        ''' given an episode with certain tags and the required request we should
            only return episodes with those tags
        '''
        Team.objects.create(name="carnivore")
        self.episode_2.set_tag_names(["carnivore"], self.user)

        patient_list = PatientList.get("carnivore")()
        self.assertEqual(
            [self.episode_2], [i for i in patient_list.get_queryset()]
        )
        serialized = patient_list.to_dict(self.user)
        self.assertEqual(len(serialized), 1)
        self.assertEqual(serialized[0]["id"], 2)
