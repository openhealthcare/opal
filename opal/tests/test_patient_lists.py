"""
Unittests for opal.core.patient_lists
"""
import datetime
import os

from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import MagicMock, PropertyMock, patch

from opal.core import exceptions
from opal.tests import models
from opal.models import Episode, Patient, UserProfile
from opal.core.test import OpalTestCase

from opal.core import patient_lists
from opal.core.patient_lists import (
    PatientList, TaggedPatientList, TabbedPatientListGroup,
    PatientListComparatorMetadata
)

"""
Begin discoverable definitions for test cases
"""


class TaggingTestPatientList(TaggedPatientList):
    display_name       = "Herbivores"
    tag                = "eater"
    subtag             = "herbivore"
    order              = 4
    icon               = 'fa-diplodocus'
    comparator_service = 'HerbivoresSortOrder'

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


class InvisibleList(TaggedPatientList):
    tag    = 'eater'
    subtag = 'shh'
    order  = 10

    @classmethod
    def visible_to(klass, user):
        if user.username == 'show me':
            return True
        else:
            return False


class TestTabbedPatientListGroup(TabbedPatientListGroup):
    member_lists = [
        TaggingTestSameTagPatientList,
        TaggingTestPatientList,
        InvisibleList
    ]


class TestEmptyTabbedPatientListGroup(TabbedPatientListGroup):
    member_lists = [InvisibleList]


class IconicList(PatientList):
    slug = 'disillusionment'
    order = 800

    @classmethod
    def get_icon(k):
        return "fa-james-dean"


class DisplayList(PatientList):
    slug = 'gastropod-mollusc'
    order = 200

    @classmethod
    def get_display_name(k):
        return 'Everyone'



"""
Begin Tests
"""


class ColumnTestCase(OpalTestCase):

    def test_set_non_inferred_attributes(self):
        c = patient_lists.Column(
            name='foo',
            title='Foo',
            singleton=True,
            icon='fa-ya',
            limit=5,
            template_path='foo/bar',
            detail_template_path='car/dar'
        )
        self.assertEqual(c.name, 'foo')
        self.assertEqual(c.title, 'Foo')
        self.assertEqual(c.single, True)
        self.assertEqual(c.icon, 'fa-ya')
        self.assertEqual(c.list_limit, 5)
        self.assertEqual(c.template_path, 'foo/bar')
        self.assertEqual(c.detail_template_path, 'car/dar')

    def test_raises_if_no_title(self):
        with self.assertRaises(ValueError):
            patient_lists.Column(name='foo', template_path='foo/bar')

    def test_raises_if_no_template_path(self):
        with self.assertRaises(ValueError):
            patient_lists.Column(title='Foo', name='foo')

    def test_get_template_path(self):
        c = patient_lists.Column(
            name='foo',
            title='Foo',
            singleton=True,
            icon='fa-ya',
            limit=5,
            template_path='foo/bar',
            detail_template_path='car/dar'
        )
        value = c.get_template_path(MagicMock('Mock Patient List'))
        self.assertEqual('foo/bar', value)

    def test_get_detail_template_path(self):
        c = patient_lists.Column(
            name='foo',
            title='Foo',
            singleton=True,
            icon='fa-ya',
            limit=5,
            template_path='foo/bar',
            detail_template_path='car/dar'
        )
        value = c.get_detail_template_path(MagicMock('Mock Patient List'))
        self.assertEqual('car/dar', value)

    def test_to_dict(self):
        c = patient_lists.Column(
            name='foo',
            title='Foo',
            singleton=True,
            icon='fa-ya',
            limit=5,
            template_path='foo/bar',
            detail_template_path='car/dar'
        )
        as_dict = c.to_dict(MagicMock('Mock Patient List'))
        self.assertEqual(as_dict['name'], 'foo')
        self.assertEqual(as_dict['title'], 'Foo')
        self.assertEqual(as_dict['single'], True)
        self.assertEqual(as_dict['icon'], 'fa-ya')
        self.assertEqual(as_dict['list_limit'], 5)
        self.assertEqual(as_dict['template_path'], 'foo/bar')
        self.assertEqual(as_dict['detail_template_path'], 'car/dar')


class ModelColumnTestCase(OpalTestCase):

    def test_sets_model(self):
        c = patient_lists.ModelColumn(
            models.Demographics
        )
        self.assertEqual(models.Demographics, c.model)

    def test_pass_in_not_a_model(self):
        with self.assertRaises(ValueError):
            patient_lists.ModelColumn(OpalTestCase)

    def test_to_dict_sets_model_column(self):
        c = patient_lists.ModelColumn(
            models.Demographics
        )
        as_dict = c.to_dict(MagicMock('Mock Patient List'))
        self.assertEqual(True, as_dict['model_column'])

    def test_get_template_path(self):
        c = patient_lists.ModelColumn(
            models.Demographics
        )
        value = c.get_template_path(MagicMock('Mock Patient List'))
        self.assertEqual(
            os.path.join('records', 'demographics.html'),
            value
        )

    def test_get_detail_template_path(self):
        c = patient_lists.ModelColumn(
            models.Demographics
        )
        value = c.get_detail_template_path(MagicMock('Mock Patient List'))
        self.assertEqual(
            os.path.join('records', 'demographics_detail.html'),
            value)



class TestPatientList(OpalTestCase):

    def setUp(self):
        self.restricted_user = User.objects.create(username='restrictedonly')
        UserProfile.objects.filter(
            user=self.restricted_user
        ).update(
            restricted_only=True
        )

    def test_unimplemented_schema(self):
        with self.assertRaises(ValueError):
            schema = PatientList().schema

    def test_unimplemented_queryset(self):
        with self.assertRaises(ValueError):
            queryset = PatientList().queryset

    def test_get_absolute_url(self):
        self.assertEqual('/#/list/carnivore', TaggingTestNotSubTag.get_absolute_url())

    def test_get_icon(self):
        self.assertEqual('fa-diplodocus', TaggingTestPatientList.get_icon())

    def test_get_display_name(self):
        self.assertEqual('Herbivores', TaggingTestPatientList.get_display_name())

    def test_get_queryset_default(self):
        mock_queryset = MagicMock('Mock Queryset')
        with patch.object(PatientList, 'queryset',
                          new_callable=PropertyMock) as queryset:
            queryset.return_value = mock_queryset
            self.assertEqual(mock_queryset, PatientList().get_queryset())

    @patch('opal.models.Episode.objects.serialised')
    def test_to_dict_passes_queryset(self, serialised):
        serialised.return_value = {}
        with patch.object(PatientList, 'get_queryset') as gq:
            with patch.object(PatientList, 'queryset', new_callable=PropertyMock) as q:
                dicted = PatientList().to_dict('my_user')
                gq.assert_called_with(user='my_user')
                self.assertEqual({}, dicted)

    def test_to_dict_inactive_episodes(self):
        p, e = self.new_patient_and_episode_please()
        e.end = datetime.date.today()
        e.save()

        class All(patient_lists.PatientList):
            display_name = 'all'
            queryset = Episode.objects.all()

        self.assertEqual(e.id, All().to_dict(self.user)[0]['id'])

    def test_visible_to(self):
        self.assertTrue(TaggingTestPatientList.visible_to(self.user))

    def test_as_menuitem(self):
        href = TaggingTestPatientList.get_absolute_url()
        menu = TaggingTestPatientList.as_menuitem()
        self.assertEqual(menu.href, href)
        self.assertEqual(menu.activepattern, href)
        self.assertEqual(menu.icon, 'fa-diplodocus')
        self.assertEqual(menu.display, 'Herbivores')

    def test_as_menuitem_from_kwargs(self):
        menu = IconicList.as_menuitem(
            href="/foo", activepattern="/f",
            icon="fa-foo", display="Foo"
        )
        self.assertEqual(menu.href, '/foo')
        self.assertEqual(menu.activepattern, '/f')
        self.assertEqual(menu.icon, 'fa-foo')
        self.assertEqual(menu.display, 'Foo')

    def test_as_menuitem_set_index(self):
        menu = TaggingTestPatientList.as_menuitem(index=-30)
        self.assertEqual(-30, menu.index)

    def test_as_menuitem_uses_getter_for_icon(self):
        menu = IconicList.as_menuitem()
        self.assertEqual('fa-james-dean', menu.icon)

    def test_as_menuitem_uses_getter_for_display(self):
        menu = DisplayList.as_menuitem()
        self.assertEqual('Everyone', menu.display)

    def test_schema_to_dicts(self):
        dicts = [
            {
                'detail_template_path': os.path.join('records', 'demographics_detail.html'),
                'icon': 'fa fa-user',
                'list_limit': None,
                'name': 'demographics',
                'single': True,
                'template_path': os.path.join('records', 'demographics.html'),
                'title': 'Demographics',
                'model_column': True
            }
        ]
        self.assertEqual(dicts, TaggingTestPatientList.schema_to_dicts())

    def test_schema_to_dicts_with_column(self):

        class ColList(patient_lists.PatientList):
            display_name = 'Columny List'

            schema = [
                patient_lists.Column(title='Foo', name='Bar',
                                     template_path='foo/bar')
            ]

        dicts = [
            {
                'detail_template_path': None,
                'icon': None,
                'list_limit': None,
                'name': 'Bar',
                'single': None,
                'template_path': 'foo/bar',
                'title': 'Foo'
            }
        ]
        self.assertEqual(dicts, ColList.schema_to_dicts())

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
        self.assertEqual(0, PatientList.order)

    def test_order_respected_by_list(self):
        expected = [
            TaggingTestNotSubTag,
            TaggingTestPatientList,
            TaggingTestSameTagPatientList,
            InvisibleList,
            DisplayList,
            IconicList
        ]
        self.assertEqual(expected, list(PatientList.list()))

    def test_get_template_names_default(self):
        self.assertEqual(['patient_lists/layouts/spreadsheet_list.html'],
                         PatientList().get_template_names())

    def test_get_template_names_overridden_proerty(self):
        self.assertEqual(['carnivore.html'], TaggingTestNotSubTag().get_template_names())

    def test_known_abstract_subclasses_not_in_list(self):
        lists = list(PatientList.list())
        self.assertNotIn(TaggedPatientList, lists)


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
        self.assertEqual(serialized[0]["id"], self.episode_2.id)

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
        self.assertEqual(serialized[0]["id"], self.episode_2.id)

    def test_list(self):
        expected = [
            TaggingTestNotSubTag,
            TaggingTestPatientList,
            TaggingTestSameTagPatientList,
            InvisibleList,
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
        expected = {'carnivore', 'herbivore', 'omnivore', 'eater', 'shh'}
        self.assertEqual(set(taglist), expected)

    def test_to_dict_inactive_episodes(self):
        # Older vesions of Opal only serialised active episodes here
        # Explicitly test to prevent a reversion
        p, e = self.new_patient_and_episode_please()
        e.set_tag_names(['carnivore'], self.user)
        self.assertEqual(e.pk, TaggingTestNotSubTag().to_dict(self.user)[0]['id'])
        e.end = datetime.date.today()
        e.save()
        self.assertEqual(1, len(TaggingTestNotSubTag().to_dict(self.user)))


class TabbedPatientListGroupTestCase(OpalTestCase):

    def test_get_member_lists(self):
        expected = [TaggingTestSameTagPatientList, TaggingTestPatientList, InvisibleList]
        members = list(TestTabbedPatientListGroup.get_member_lists())
        self.assertEqual(expected, members)

    def test_get_member_lists_for_user(self):
        expected = [TaggingTestSameTagPatientList, TaggingTestPatientList]
        members = list(TestTabbedPatientListGroup.get_member_lists_for_user(self.user))
        self.assertEqual(expected, members)

    def test_get_member_lists_for_user_with_restricted_lists(self):
        expected = [TaggingTestSameTagPatientList, TaggingTestPatientList, InvisibleList]
        user = self.user
        user.username = 'show me'
        members = list(TestTabbedPatientListGroup.get_member_lists_for_user(user))
        self.assertEqual(expected, members)

    def test_for_list(self):
        self.assertEqual(TestTabbedPatientListGroup,
                         TabbedPatientListGroup.for_list(InvisibleList))

    def test_for_list_raises_if_non_list_passed(self):
        with self.assertRaises(ValueError):
            TabbedPatientListGroup.for_list(None)
        with self.assertRaises(ValueError):
            TabbedPatientListGroup.for_list(2)
        with self.assertRaises(ValueError):
            TabbedPatientListGroup.for_list('Carnivores')
        with self.assertRaises(ValueError):
            TabbedPatientListGroup.for_list(OpalTestCase)

    def test_visible_to(self):
        self.assertTrue(TestTabbedPatientListGroup.visible_to(self.user))

    def test_invisible_to_if_member_lists_for_user_empty(self):
        self.assertFalse(TestEmptyTabbedPatientListGroup.visible_to(self.user))


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


class ComparatorMetadataTestCase(OpalTestCase):

    def test_to_dict(self):
        comparators = PatientListComparatorMetadata.to_dict(user=self.user)
        self.assertEqual({'eater-herbivore': 'HerbivoresSortOrder'}, comparators['patient_list_comparators'])
