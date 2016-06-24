"""
Unittests for opal.core.patient_lists
"""
from django.contrib.auth.models import User
from mock import MagicMock, PropertyMock, patch

from opal.core import exceptions
from opal.tests import models
from opal.models import Patient, Team, UserProfile
from opal.core.test import OpalTestCase

from opal.core import patient_lists
from opal.core.patient_lists import PatientList, TaggedPatientList


class TaggingTestPatientList(TaggedPatientList):
    display_name = "Herbivores"
    tag = "eater"
    subtag = "herbivore"
    order = 4

    schema = [
        models.Demographics,
    ]


class TaggingTestNotSubTag(TaggedPatientList):
    display_name = 'Carnivores'
    direct_add = False
    tag = "carnivore"
    order = 1
    template_name = 'carnivore.html'

    schema = [
        models.Demographics,
    ]


class TaggingTestSameTagPatientList(TaggedPatientList):
        # we shouldn't have duplicate tags so lets check that by
        # having another patient list with the same parent tag
        # but different subtrags
        display_name = "Omnivore"
        tag = "eater"
        subtag = "omnivore"
        order = 5

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
        with patch.object(PatientList, 'queryset',
                          new_callable=PropertyMock) as queryset:
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

    def test_order(self):
        self.assertEqual(1, TaggingTestNotSubTag.order)

    def test_order_unimplemented(self):
        self.assertEqual(None, PatientList.order)

    def test_order_respected_by_list(self):
        expected = [
            TaggingTestNotSubTag,
            TaggingTestPatientList,
            TaggingTestSameTagPatientList
        ]
        self.assertEqual(expected, list(PatientList.list()))

    def test_get_template_names_default(self):
        self.assertEqual(['patient_lists/spreadsheet_list.html'], PatientList().get_template_names())

    def test_get_template_names_overridden_proerty(self):
        self.assertEqual(['carnivore.html'], TaggingTestNotSubTag().get_template_names())

    def test_known_abstract_subclasses_not_in_list(self):
        lists = list(PatientList.list())
        self.assertNotIn(TaggedPatientList, lists)

class FirstListMetadataTestCase(OpalTestCase):

    def test_first_list_slug(self):
        slug = patient_lists.FirstListMetadata.to_dict(user=self.user)
        self.assertEqual({'first_list_slug': 'carnivore'}, slug)

    def test_first_list_slug_no_lists_for_user(self):
        def nongen():
            for x in range(0, 0):
                yield x

        with patch.object(patient_lists.PatientList, 'for_user') as for_user:
            for_user.return_value = nongen()
            slug = patient_lists.FirstListMetadata.to_dict(user=self.user)
            self.assertEqual({'first_list_slug': ''}, slug)


class TestTaggedPatientList(OpalTestCase):


    def setUp(self):
        self.patient = Patient.objects.create()
        self.episode_1 = self.patient.create_episode()
        self.episode_2 = self.patient.create_episode()

    def test_default_direct_add(self):
        self.assertTrue(TaggingTestPatientList.direct_add)

    def test_tagging_set_with_subtag(self):
        ''' given an episode with certain tags and the required request we should
            only return episodes with those tags
        '''
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
        self.episode_2.set_tag_names(["carnivore"], self.user)

        patient_list = PatientList.get("carnivore")()
        self.assertEqual(
            [self.episode_2], [i for i in patient_list.get_queryset()]
        )
        serialized = patient_list.to_dict(self.user)
        self.assertEqual(len(serialized), 1)
        self.assertEqual(serialized[0]["id"], 2)

    def test_list(self):
        expected = [
            TaggingTestNotSubTag,
            TaggingTestPatientList,
            TaggingTestSameTagPatientList
        ]
        self.assertEqual(expected, list(TaggedPatientList.list()))

    def test_invalid_tag_name(self):
        with self.assertRaises(exceptions.InvalidDiscoverableFeatureError):
            class MyList(TaggedPatientList):
                tag = 'foo-bar'

    def test_invalid_subtag_name(self):
        with self.assertRaises(exceptions.InvalidDiscoverableFeatureError):
            class MyList(TaggedPatientList):
                tag = 'foo'
                subtag = 'one-two'

    def test_get_tag_names(self):

        taglist = TaggedPatientList.get_tag_names()
        expected = {'carnivore', 'herbivore', 'omnivore', 'eater'}
        self.assertEqual(set(taglist), expected)
