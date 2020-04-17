"""
Tests for the OPAL API
"""
import json
from six.moves import reload_module

from datetime import date, timedelta, datetime

from django.utils import timezone
from django.contrib.auth.models import User
from django.test import TestCase
from django.db import DataError
from django.http import Http404
from django.contrib.contenttypes.models import ContentType
from unittest.mock import patch, MagicMock

from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from rest_framework import status

from opal import models
from opal.tests.models import (
    Colour, PatientColour, HatWearer, Hat, Demographics
)
from opal.core import metadata
from opal.core.test import OpalTestCase
from opal.core.views import json_response
from opal.core.exceptions import APIError

# this is used just to import the class for
# EpisodeListApiTestCase and OptionsViewSetTestCase
from opal.tests.test_patient_lists import TaggingTestPatientList # flake8: noqa

from opal.core import api

class LoginRequredTestCase(OpalTestCase):
    """
    We expect almost all views to 401
    """
    def setUp(self):
        self.patient, self.episode = self.new_patient_and_episode_please()
        self.request = self.rf.get("/")
        self.hat_wearer = HatWearer.objects.create(episode=self.episode)

    def get_urls(self):
        return [
            reverse('record-list', request=self.request),
            reverse('referencedata-list', request=self.request),
            reverse('metadata-list', request=self.request),
            reverse('episode-list', request=self.request),
            reverse('userprofile-list', request=self.request),
            reverse(
                'patient-detail',
                kwargs=dict(pk=self.patient.id),
                request=self.request
            ),
            reverse(
                'hat_wearer-detail',
                kwargs=dict(pk=self.hat_wearer.id),
                request=self.request
            )
        ]

    def test_401(self):
        for url in self.get_urls():
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                401
            )


class TestDecorators(OpalTestCase):
    def test_patient_from_pk(self):
        patient, _ = self.new_patient_and_episode_please()
        some_func = MagicMock()
        request = MagicMock()
        some_self = MagicMock()
        decorated = api.patient_from_pk(some_func)
        decorated(some_self, request, patient.id)
        some_func.assert_called_once_with(some_self, request, patient)

    def test_no_patient_exists_exception(self):
        self.assertEqual(models.Patient.objects.count(), 0)
        with self.assertRaises(Http404) as e:
            some_func = MagicMock()
            request = MagicMock()
            some_self = MagicMock()
            decorated = api.patient_from_pk(some_func)
            decorated(some_self, request, 1)
        self.assertEqual(
            str(e.exception),
            "No Patient matches the given query."
        )


class OPALRouterTestCase(TestCase):

    def test_default_base_name(self):
        class ViewSet:
            base_name = 'the name'
        self.assertEqual(api.OPALRouter().get_default_base_name(ViewSet), 'the name')

    def test_default_base_name_unset(self):
        class ColourViewSet:
            queryset = Colour.objects.all()
        self.assertEqual(api.OPALRouter().get_default_base_name(ColourViewSet), 'colour')


class RecordTestCase(TestCase):

    @patch('opal.core.api.schemas')
    def test_records(self, schemas):
        schemas.list_records.return_value = [{}]
        self.assertEqual([{}], api.RecordViewSet().list(None).data)


class ReferenceDataViewSetTestCase(OpalTestCase):

    def setUp(self):
        self.top = Hat.objects.create(name="top")
        self.bowler = Hat.objects.create(name="bowler")
        self.synonym_name = "high"
        self.user = User.objects.create(username='testuser')
        content_type = ContentType.objects.get_for_model(Hat)
        models.Synonym.objects.get_or_create(
            content_type=content_type,
            object_id=self.top.id,
            name=self.synonym_name
        )
        mock_request = MagicMock(name='mock request')
        mock_request.user = self.user
        self.request = mock_request
        self.viewset = api.ReferenceDataViewSet()
        self.viewset.request = mock_request

    def test_list(self):
        self.response = self.viewset.list(self.request)
        result = self.response.data
        self.assertIn("hat", result)
        self.assertEqual(set(result["hat"]), {"top", "bowler", "high"})
        self.assertEqual(self.response.status_code, 200)

    def test_get(self):
        response = self.viewset.retrieve(self.request, pk='hat')
        self.assertEqual(set(response.data), {"top", "bowler", "high"})
        self.assertEqual(response.status_code, 200)

    def test_get_does_not_exist(self):
        response = self.viewset.retrieve(self.request, pk='notalookuplist')
        self.assertEqual(response.status_code, 404)


class MetadataViewSetTestCase(OpalTestCase):

    def test_list(self):
        mock_request = MagicMock(name='mock request')
        mock_request.user = self.user
        response = api.MetadataViewSet().list(mock_request)
        self.assertEqual(200, response.status_code)
        for s in metadata.Metadata.list():
            for key, value in s.to_dict(user=self.user).items():
                self.assertEqual(response.data[key], value)

    def test_retrieve(self):
        mock_request = MagicMock(name='Mock Request')
        mock_request.user = self.user
        mock_metadata = MagicMock(name='Mock Metadata')
        mock_metadata.to_dict.return_value = {'settings': True}
        with patch.object(api.metadata.Metadata, 'get') as mock_get:
            mock_get.return_value = mock_metadata
            response = api.MetadataViewSet().retrieve(mock_request, pk='mymetadata')
            self.assertEqual({'settings': True}, response.data)


    def test_retrieve_nonexistent_metadata(self):
        mock_request = MagicMock(name='mock request')
        mock_request.user = self.user
        response = api.MetadataViewSet().retrieve(mock_request, pk='notarealmetadata')
        self.assertEqual(404, response.status_code)


class SubrecordTestCase(OpalTestCase):

    def setUp(self):
        self.patient, self.episode = self.new_patient_and_episode_please()

        class OurViewSet(api.SubrecordViewSet):
            base_name = 'colour'
            model     = Colour

        class OurPatientViewSet(api.SubrecordViewSet):
            base_name = 'patientcolour'
            model = PatientColour


        self.model = Colour
        self.viewset = OurViewSet
        self.patientviewset = OurPatientViewSet
        self.assertTrue(
            self.client.login(
                username=self.user.username, password=self.PASSWORD
            )
        )
        # We don't want API Errors to print noise at the terminal so let's monkey
        # patch StreamHandler.emit
        from logging import StreamHandler
        self._emit = StreamHandler.emit
        StreamHandler.emit = MagicMock('Mock Stream Handler')

    def tearDown(self):
        from logging import StreamHandler
        StreamHandler.emit = self._emit

    def test_list(self):
        response = self.viewset().list(None)
        self.assertEqual([], json.loads(response.content.decode('UTF-8')))

    def test_list_with_some_contents(self):
        c1 = Colour.objects.create(
            name="blue", episode=self.episode
        )
        c2 = Colour.objects.create(
            name="red", episode=self.episode
        )
        mock_request = MagicMock(name='mock request')
        mock_request.user = self.user
        response = self.viewset().list(mock_request)
        data = [
            {
                u'consistency_token': u'',
                u'created': None,
                u'created_by_id': None,
                u'episode_id': self.episode.id,
                u'id': c1.id,
                u'name': u'blue',
                u'updated': None,
                u'updated_by_id': None
            },
            {
                u'consistency_token': u'',
                u'created': None,
                u'created_by_id': None,
                u'episode_id': self.episode.id,
                u'id': c2.id,
                u'name': u'red',
                u'updated': None,
                u'updated_by_id': None
            }
        ]
        self.assertEqual(data, json.loads(response.content.decode('UTF-8')))

    def test_create(self):
        mock_request = MagicMock(name='mock request')
        mock_request.user = self.user
        mock_request.data = {'name': 'blue', 'episode_id': self.episode.pk}
        response = self.viewset().create(mock_request)
        colour = Colour.objects.get()
        self.assertEqual(date.today(), colour.created.date())
        self.assertEqual(self.user, colour.created_by)
        self.assertIsNone(colour.updated)
        self.assertIsNone(colour.updated_by)
        self.assertEqual('blue', json.loads(response.content.decode('UTF-8'))['name'])

    def test_create_patient_subrecord(self):
        mock_request = MagicMock(name='mock request')
        mock_request.user = self.user
        mock_request.data = {'name': 'blue', 'episode_id': self.episode.pk,
                             'patient_id': self.patient.pk}
        response = self.patientviewset().create(mock_request)
        self.assertEqual('blue', json.loads(response.content.decode('UTF-8'))['name'])

    def test_create_nonexistant_episode(self):
        mock_request = MagicMock(name='mock request')
        mock_request.data = {'name': 'blue', 'episode_id': 56785}
        mock_request.user = self.user
        response = self.viewset().create(mock_request)
        self.assertEqual(400, response.status_code)

    def test_create_unexpected_field(self):
        data = {'name': 'blue', 'hue': 'enabled', 'episode_id': self.episode.pk}
        request = self.rf.get("/")
        url = reverse("colour-list", request=request)

        with self.assertRaises(APIError) as e:
            response = self.client.post(url, data=data)

    def test_retrieve(self):
        colour = Colour.objects.create(
            episode=self.episode
        )
        expected = {
            u'consistency_token': u'',
            u'created'          : None,
            u'created_by_id'    : None,
            u'episode_id'       : self.episode.id,
            u'id'               : colour.id,
            u'name'             : None,
            u'updated'          : None,
            u'updated_by_id'    : None
        }
        response = self.viewset().retrieve(MagicMock(name='request'), pk=colour.id)
        response_decoded = json.loads(response.content.decode('UTF-8'))
        self.assertEqual(expected, response_decoded)

    def test_retrieve_with_empty_fk_or_ft(self):
        self.maxDiff = None
        instance = self.patient.demographics_set.get()
        class DemographicsViewSet(api.SubrecordViewSet):
            base_name = 'demographics'
            model     = Demographics

        expected = {
            u'consistency_token': u'',
            u'created'          : None,
            u'created_by_id'    : None,
            u'patient_id'       : self.patient.id,
            u'id'               : instance.id,
            u'updated'          : None,
            u'updated_by_id'    : None,
            u'date_of_birth'    : None,
            u'date_of_death'    : None,
            u'death_indicator'  : False,
            u'ethnicity'        : '',
            u'birth_place'      : '',
            u'first_name'       : '',
            u'gp_practice_code' : None,
            u'hospital_number'  : '',
            u'marital_status'   : '',
            u'middle_name'      : None,
            u'nhs_number'       : None,
            u'post_code'        : None,
            u'religion'         : None,
            u'sex'              : '',
            u'surname'          : '',
            u'title'            : ''
        }
        response = DemographicsViewSet().retrieve(MagicMock(name='request'), pk=instance.id)
        response_decoded = json.loads(response.content.decode('UTF-8'))
        self.assertEqual(expected, response_decoded)

    def test_with_defined_api_name(self):
        with patch.object(self.model, "get_api_name") as mock_api_name:
            mock_api_name.return_value = "something"
            reload_module(api)
            api.initialize_router()
            router = api.router
            self.assertIn(
                "something",
                {i[0] for i in router.registry}
            )

    def test_update(self):
        created = timezone.now() - timedelta(1)
        colour = Colour.objects.create(
            name='blue',
            episode=self.episode,
            created_by=self.user,
            created=created,
        )
        mock_request = MagicMock(name='mock request')
        mock_request.data = {
            'name': 'green',
            'episode_id': self.episode.pk,
            'id': colour.pk,
            'consistency_token': colour.consistency_token,
        }
        mock_request.user = self.user
        response = self.viewset().update(mock_request, pk=colour.pk)

        updated_colour = Colour.objects.get()
        self.assertEqual(created, updated_colour.created)
        self.assertEqual(self.user, updated_colour.created_by)
        self.assertEqual(date.today(), updated_colour.updated.date())
        self.assertEqual(202, response.status_code)
        self.assertEqual('green', json.loads(response.content.decode('UTF-8'))['name'])

    def test_update_item_changed(self):
        created = timezone.now() - timedelta(1)

        colour = Colour.objects.create(
            name='blue',
            episode=self.episode,
            consistency_token='frist',
            created_by=self.user,
            created=created,
        )
        mock_request = MagicMock(name='mock request')
        mock_request.data = {
            'name': 'green',
            'episode_id': self.episode.pk,
            'id': colour.pk,
            'consistency_token': 'wat'
        }
        mock_request.user = self.user
        response = self.viewset().update(mock_request, pk=colour.pk)
        colour = Colour.objects.get()
        self.assertEqual(created, colour.created)
        self.assertEqual(self.user, colour.created_by)
        self.assertIsNone(colour.updated)
        self.assertIsNone(colour.updated_by)
        self.assertEqual(409, response.status_code)

    def test_update_nonexistent(self):
        response = self.viewset().update(MagicMock(), pk=67757)
        self.assertEqual(404, response.status_code)

    def test_update_unexpected_field(self):
        colour = Colour.objects.create(name='blue', episode=self.episode)
        mock_request = MagicMock(name='mock request')
        mock_request.data = {
            'name'             : 'green',
            'hue'              : 'sea',
            'episode_id'       : self.episode.pk,
            'id'               : colour.pk,
            'consistency_token': colour.consistency_token
        }
        mock_request.user = self.user
        response = self.viewset().update(mock_request, pk=colour.pk)
        self.assertEqual(400, response.status_code)

    def test_update_no_consistency_token(self):
        colour = Colour.objects.create(name='blue', episode=self.episode)
        colour.set_consistency_token()
        colour.save()
        mock_request = MagicMock(name='mock request')
        mock_request.data = {
            'name'             : 'green',
            'episode_id'       : self.episode.pk,
            'id'               : colour.pk,
        }
        mock_request.user = self.user
        response = self.viewset().update(mock_request, pk=colour.pk)
        message = json.loads(response.content.decode('UTF-8'))
        self.assertEqual(message['error'], 'Missing consistency token')

    def test_delete(self):
        colour = Colour.objects.create(episode=self.episode)
        mock_request = MagicMock(name='mock request')
        mock_request.user = self.user
        response = self.viewset().destroy(mock_request, pk=colour.pk)
        self.assertEqual(202, response.status_code)
        with self.assertRaises(Colour.DoesNotExist):
            c2 = Colour.objects.get(pk=colour.pk)

    def test_delete_nonexistent(self):
        response = self.viewset().destroy(MagicMock(name='request'), pk=567)
        self.assertEqual(404, response.status_code)


class ManyToManyTestSubrecordWithLookupListTest(TestCase):

    def setUp(self):
        self.patient = models.Patient.objects.create()
        self.episode = models.Episode.objects.create(patient=self.patient)
        self.user = User.objects.create(username='testuser')

        class ManyToManyViewSet(api.SubrecordViewSet):
            base_name = 'hatwearer'
            model = HatWearer

        self.model = HatWearer
        self.viewset = ManyToManyViewSet
        self.bowler = Hat.objects.create(name="bowler")
        self.top = Hat.objects.create(name="top")
        self.synonym_name = "high"
        content_type = ContentType.objects.get_for_model(Hat)
        models.Synonym.objects.get_or_create(
            content_type=content_type,
            object_id=self.top.id,
            name=self.synonym_name
        )

    def create_hat_wearer(self, *hats):
        hat_wearer = HatWearer.objects.create(
            episode=self.episode,
            name="Jane"
        )
        hat_wearer.hats.add(*hats)
        return hat_wearer

    def create_mock_request(self, **kwargs):
        mock_request = MagicMock(name='mock request')
        mock_request.user = self.user

        mock_request.data = {
            'name': 'Jane',
            'episode_id': self.episode.id,
        }
        mock_request.data.update(kwargs)
        return mock_request

    def test_many_to_many_create(self):
        mock_request = self.create_mock_request(
            hats=[self.bowler.name, self.top.name]
        )
        self.viewset().create(mock_request)
        hat_wearer = HatWearer.objects.get(name="Jane")
        self.assertEqual(hat_wearer.episode.id, self.episode.id)
        self.assertEqual(list(hat_wearer.hats.all()), [self.bowler, self.top])

    def test_many_to_many_synonym_create(self):
        mock_request = self.create_mock_request(
            hats=[self.synonym_name]
        )
        self.viewset().create(mock_request)
        hat_wearer = HatWearer.objects.get(name="Jane")
        self.assertEqual(hat_wearer.episode.id, self.episode.id)
        self.assertEqual(list(hat_wearer.hats.all()), [self.top])

    def test_many_to_many_synonym_create_unique(self):
        mock_request = self.create_mock_request(
            hats=[self.synonym_name, self.top.name]
        )
        self.viewset().create(mock_request)
        hat_wearer = HatWearer.objects.get(name="Jane")
        self.assertEqual(hat_wearer.episode.id, self.episode.id)
        self.assertEqual(list(hat_wearer.hats.all()), [self.top])

    def test_many_to_many_update_add(self):
        hat_wearer = self.create_hat_wearer(self.bowler)
        mock_request = self.create_mock_request(
            hats=[self.bowler.name, self.top.name],
            consistency_token='wat',
            id=hat_wearer.id
        )

        self.viewset().update(mock_request, pk=hat_wearer.pk)
        hat_wearer = HatWearer.objects.get(name="Jane")
        self.assertEqual(hat_wearer.episode.id, self.episode.id)
        self.assertEqual(list(hat_wearer.hats.all()), [self.bowler, self.top])

    def test_many_to_many_update_synonym(self):
        hat_wearer = self.create_hat_wearer(self.bowler)
        mock_request = self.create_mock_request(
            hats=[self.bowler.name, self.synonym_name],
            consistency_token='wat',
            id=hat_wearer.id
        )

        self.viewset().update(mock_request, pk=hat_wearer.pk)
        hat_wearer = HatWearer.objects.get(name="Jane")
        self.assertEqual(hat_wearer.episode.id, self.episode.id)
        self.assertEqual(list(hat_wearer.hats.all()), [self.bowler, self.top])

    def test_many_to_many_update_delete(self):
        hat_wearer = self.create_hat_wearer(self.bowler)
        mock_request = self.create_mock_request(
            hats=[self.bowler.name],
            id=hat_wearer.id
        )
        self.viewset().update(mock_request, pk=hat_wearer.pk)
        hat_wearer = HatWearer.objects.get(name="Jane")
        self.assertEqual(hat_wearer.episode.id, self.episode.id)
        self.assertEqual(list(hat_wearer.hats.all()), [self.bowler])

    def test_normal_delete(self):
        hat_wearer = self.create_hat_wearer(self.bowler, self.top)
        mock_request = MagicMock(name='mock request')
        mock_request.user = self.user
        self.viewset().destroy(mock_request, pk=hat_wearer.pk)
        self.assertFalse(HatWearer.objects.filter(name="Jane").exists())

    def test_removal_of_unknown_field(self):
        """
        we should be transactional, if we blow up, nothing should be saved
        """
        hat_wearer = self.create_hat_wearer(self.bowler)
        mock_request = self.create_mock_request(
            hats=[self.top.name, "fake hat"],
            id=hat_wearer.id
        )
        response = self.viewset().update(mock_request, pk=hat_wearer.pk)
        self.assertEqual(400, response.status_code)
        hw = HatWearer.objects.get(name=u"Jane")
        hat_names = hw.hats.all().values_list("name", flat=True)
        self.assertEqual(list(hat_names), [self.bowler.name])


class UserProfileTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.mock_request = MagicMock(name='request')
        self.mock_request.user = self.user

    def test_user_profile(self):
        response = api.UserProfileViewSet().list(self.mock_request)
        expected = {
            'readonly'   : False,
            'can_extract': False,
            'filters'    : [],
            'roles'      : {'default': []},
            'full_name'  : '',
            'avatar_url' : 'http://gravatar.com/avatar/5d9c68c6c50ed3d02a2fcf54f63993b6?s=80&r=g&d=identicon',
            'user_id'    : self.user.id
        }
        self.assertEqual(expected, response.data)

    def test_user_profile_readonly(self):
        profile = self.user.profile
        profile.readonly = True
        profile.save()
        response = api.UserProfileViewSet().list(self.mock_request)
        self.assertEqual(True, response.data['readonly'])


class UserTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.mock_request = MagicMock(name='request')
        self.mock_request.user = self.user

    def test_list(self):
        response = api.UserViewSet().list(self.mock_request)
        self.assertEqual([self.user.profile.to_dict()], response.data)

    def test_retrieve(self):
        response = api.UserViewSet().retrieve(
            self.mock_request, pk=self.user.id
        )
        self.assertEqual(self.user.profile.to_dict(), response.data)


class TaggingTestCase(TestCase):

    def setUp(self):
        self.patient = models.Patient.objects.create()
        self.episode = models.Episode.objects.create(patient=self.patient)
        self.user    = User.objects.create(username='testuser')
        self.mock_request = MagicMock(name='request')
        self.mock_request.user = self.user

    def test_retrieve_tags(self):
        self.episode.set_tag_names(['micro'], self.user)
        response = api.TaggingViewSet().retrieve(self.mock_request, pk=self.episode.pk)
        self.assertEqual(200, response.status_code)
        self.assertEqual(True, response.data['micro'])

    def test_tag_episode(self):
        self.assertEqual(list(self.episode.get_tag_names(self.user)), [])
        self.mock_request.data = {'micro': True}
        response = api.TaggingViewSet().update(self.mock_request, pk=self.episode.pk)
        self.assertEqual(202, response.status_code)
        self.assertEqual(list(self.episode.get_tag_names(self.user)), ['micro'])
        tag = models.Tagging.objects.get()
        self.assertEqual(tag.created.date(), timezone.now().date())
        self.assertEqual(tag.created_by, self.user)
        self.assertIsNone(tag.updated_by)
        self.assertIsNone(tag.updated)

    def test_tag_episoe_with_id(self):
        self.assertEqual(list(self.episode.get_tag_names(self.user)), [])
        self.mock_request.data = {'micro': True, 'id': self.episode.id}
        response = api.TaggingViewSet().update(self.mock_request, pk=self.episode.pk)
        self.assertEqual(202, response.status_code)
        self.assertEqual(list(self.episode.get_tag_names(self.user)), ['micro'])
        tag = models.Tagging.objects.get()
        self.assertEqual(tag.created.date(), timezone.now().date())
        self.assertEqual(tag.created_by, self.user)
        self.assertIsNone(tag.updated_by)
        self.assertIsNone(tag.updated)

    def test_untag_episode(self):
        self.assertEqual(list(self.episode.get_tag_names(self.user)), [])
        self.episode.set_tag_names(['micro'], self.user)
        self.mock_request.data = {'micro': False}
        response = api.TaggingViewSet().update(self.mock_request, pk=self.episode.pk)
        self.assertEqual(202, response.status_code)
        self.assertEqual(list(self.episode.get_tag_names(self.user)), [])

    def test_mixed_tagging_truthiness(self):
        self.assertEqual(list(self.episode.get_tag_names(self.user)), [])
        self.episode.set_tag_names(['micro'], self.user)
        self.mock_request.data = {'micro': False, 'inpatient': True}
        response = api.TaggingViewSet().update(self.mock_request, pk=self.episode.pk)
        self.assertEqual(['inpatient'], self.episode.get_tag_names(self.user))

    def test_tag_nonexistent_episode(self):
        response = api.TaggingViewSet().update(self.mock_request, pk=56576)
        self.assertEqual(404, response.status_code)


class EpisodeTestCase(OpalTestCase):

    def setUp(self):
        super(EpisodeTestCase, self).setUp()
        self.patient, self.episode = self.new_patient_and_episode_please()
        self.demographics = self.patient.demographics()

        # add a date to make sure serialisation works as expected
        self.demographics.date_of_birth = date(2010, 1, 1)
        self.demographics.created = timezone.now()
        self.episode.start = date(2014, 1, 14)
        self.episode.end = date(2014, 1, 15)
        self.episode.active = True
        self.episode.save()
        self.user = User.objects.create(username='testuser')
        self.mock_request = MagicMock(name='request')
        self.mock_request.user = self.user
        self.mock_request.query_params = {}
        self.expected = self.episode.to_dict(self.user)
        self.expected["start"] = "14/01/2014"
        self.expected["end"] = "15/01/2014"

    def test_retrieve_episode(self):
        response = json.loads(api.EpisodeViewSet().retrieve(self.mock_request, pk=self.episode.pk).content.decode('UTF-8'))
        self.assertEqual(self.expected, response)

    def test_retrieve_nonexistent_episode(self):
        response = api.EpisodeViewSet().retrieve(self.mock_request, pk=678687)
        self.assertEqual(404, response.status_code)

    def test_list(self):
        response = api.EpisodeViewSet().list(self.mock_request)
        self.assertEqual(200, response.status_code)
        response_content = json.loads(response.content.decode('UTF-8'))[0]
        self.assertEqual(self.expected, response_content)

    def test_list_unauthenticated(self):
        pass #TODO TEST THIS

    def test_create_existing_patient(self):
        self.demographics.hospital_number = '123123123'
        self.demographics.save()
        self.mock_request.data = {
            "tagging"          : { "micro":True },
            "start": "14/01/2015",
            "demographics"     : {
                "hospital_number": self.demographics.hospital_number
            }
        }
        response = api.EpisodeViewSet().create(self.mock_request)
        self.assertEqual(201, response.status_code)
        self.assertEqual(2, self.patient.episode_set.count())
        self.assertEqual("14/01/2015", json.loads(response.content.decode('UTF-8'))['start'])

    def test_create_new_patient(self):
        pcount = models.Patient.objects.filter(
            demographics__hospital_number="999000999").count()
        self.assertEqual(0, pcount)
        self.mock_request.data = {
            "tagging"           : { "micro":True },
            "start" : "14/01/2015",
            "demographics"      : {
                "hospital_number": "999000999"
            }
        }
        response = api.EpisodeViewSet().create(self.mock_request)
        episode = models.Episode.objects.get(
            patient__demographics__hospital_number="999000999"
        )
        self.assertEqual(
            episode.created_by,
            self.mock_request.user
        )
        self.assertEqual(
            episode.created.date(),
            timezone.now().date()
        )
        self.assertIsNone(episode.updated)
        self.assertIsNone(episode.updated_by)

        self.assertEqual(
            len(response.data["demographics"]),
            1,
        )

        self.assertTrue(
            response.data["tagging"][0]["micro"]
        )

        self.assertEqual(201, response.status_code)
        pcount = models.Patient.objects.filter(
            demographics__hospital_number="999000999").count()
        self.assertEqual(1, pcount)

    def test_create_without_hospital_number(self):
        self.mock_request.data = {
            "tagging"           : { "micro":True },
            "start" : "14/01/2015",
            "demographics"      : {
                "first_name": "James"
            }
        }
        response = api.EpisodeViewSet().create(self.mock_request)
        self.assertEqual(1, Demographics.objects.filter(first_name='James').count())

    def test_create_sets_demographics(self):
        pcount = models.Patient.objects.filter(
            demographics__hospital_number="9999000999").count()
        self.assertEqual(0, pcount)
        self.mock_request.data = {
            "tagging"                : { "micro":True },
            "start"      : "14/01/2015",
            "demographics" : {
                "first_name": "Alain",
                "surname": "Anderson",
                "sex": "Male",
                "hospital_number": "9999000999",
            }
        }
        response = api.EpisodeViewSet().create(self.mock_request)
        patient = models.Patient.objects.get(
            demographics__hospital_number="9999000999"
        )
        demographics = patient.demographics()
        self.assertEqual("Alain", demographics.first_name)
        self.assertEqual("Anderson", demographics.surname)
        self.assertEqual("Male", demographics.sex)

    def test_create_sets_location(self):
        pcount = models.Patient.objects.filter(
            demographics__hospital_number="9999000999").count()
        self.assertEqual(0, pcount)
        self.mock_request.data = {
            "tagging"                : { "micro":True },
            "start"      : "14/01/2015",
            "demographics" : {
                "hospital_number": "9999000999",
            },
            "location": {
                "ward": "West",
                "bed" : "7"
            }
        }
        response = api.EpisodeViewSet().create(self.mock_request)
        patient = models.Patient.objects.get(
            demographics__hospital_number="9999000999")
        location = patient.episode_set.get().location_set.get()
        self.assertEqual("West", location.ward)
        self.assertEqual("7", location.bed)

    def test_create_sets_tagging(self):
        pcount = models.Patient.objects.filter(
            demographics__hospital_number="9999000999").count()
        self.assertEqual(0, pcount)
        self.mock_request.data = {
            "tagging"                : { "micro":True },
            "start"      : "14/01/2015",
            "demographics" : {
                "hospital_number": "9999000999",
            },
            "location": {
                "ward": "West",
                "bed" : "7"
            }
        }
        response = api.EpisodeViewSet().create(self.mock_request)
        patient = models.Patient.objects.get(
            demographics__hospital_number="9999000999")
        episode = patient.episode_set.get()
        tags = episode.get_tag_names(self.user)
        self.assertEqual(u'micro', tags[0])
        self.assertEqual(1, len(tags))

    def test_create_sets_tagging_with_falsy_tags(self):
        pcount = models.Patient.objects.filter(
            demographics__hospital_number="9999000999").count()
        self.assertEqual(0, pcount)
        self.mock_request.data = {
            "tagging"                : { "micro":True, 'inpatient': False },
            "start"      : "14/01/2015",
            "demographics" : {
                "hospital_number": "9999000999",
            },
            "location": {
                "ward": "West",
                "bed" : "7"
            }
        }
        response = api.EpisodeViewSet().create(self.mock_request)
        patient = models.Patient.objects.get(
            demographics__hospital_number="9999000999")
        episode = patient.episode_set.get()
        tags = episode.get_tag_names(self.user)
        self.assertEqual(['micro'], tags)
        self.assertEqual(1, len(tags))

    def test_can_set_stage(self):
        self.mock_request.data = {
            "tagging"      : { "micro":True },
            "start"        : "14/01/2015",
            "stage"        : "Inpatient",
            "demographics" : {
                "hospital_number": "9999000999",
            },
            "location"     : {
                "ward": "West",
                "bed" : "7"
            }
        }
        response = api.EpisodeViewSet().create(self.mock_request)
        patient = models.Patient.objects.get(
            demographics__hospital_number="9999000999")
        episode = patient.episode_set.get()
        self.assertEqual('Inpatient', episode.stage)

    def test_cant_set_invalid_stage(self):
        self.mock_request.data = {
            "tagging"      : { "micro":True },
            "start"        : "14/01/2015",
            "stage"        : "Whoops",
            "demographics" : {
                "hospital_number": "9999000999",
            },
            "location"     : {
                "ward": "West",
                "bed" : "7"
            }
        }
        with self.assertRaises(ValueError):
            response = api.EpisodeViewSet().create(self.mock_request)

    def test_update(self):
        patient, episode = self.new_patient_and_episode_please()
        self.assertEqual(None, episode.start)
        self.mock_request.data = {"start": "14/01/2015"}
        response = api.EpisodeViewSet().update(self.mock_request, pk=episode.pk)
        e = models.Episode.objects.get(pk=episode.pk)
        self.assertEqual(date(2015, 1, 14), e.start)
        response_dict = json.loads(response.content.decode('UTF-8'))
        self.assertEqual(response_dict["start"], "14/01/2015")
        self.assertEqual(
            len(response_dict["demographics"]),
            1
        )

    def test_update_nonexistent(self):
        self.mock_request.data = {"start": "14/01/2015"}
        response = api.EpisodeViewSet().update(self.mock_request, pk=8993939)
        self.assertEqual(404, response.status_code)

    def test_update_missing_consistency_token(self):
        p, e = self.new_patient_and_episode_please()
        e.set_consistency_token()
        e.save()
        self.mock_request.data = {
            "start": "14/01/2015"
        }
        response = api.EpisodeViewSet().update(self.mock_request, pk=e.pk)
        message = json.loads(response.content.decode('UTF-8'))
        self.assertEqual(message['error'], 'Missing consistency token')
        self.assertEqual(400, response.status_code)

    def test_update_consistency_error(self):
        patient, episode = self.new_patient_and_episode_please()
        episode.consistency_token = 'FFFF'
        episode.save()
        self.mock_request.data = {
            "start": "14/01/2015",
            "consistency_token": "EEEE"
        }
        response = api.EpisodeViewSet().update(self.mock_request, pk=episode.pk)
        self.assertEqual(409, response.status_code)


class PatientTestCase(OpalTestCase):
    def setUp(self):
        self.patient      = models.Patient.objects.create()
        self.mock_request = MagicMock(name='request')
        self.mock_request.user = self.user

    def test_retrieve_patient(self):
        response = api.PatientViewSet().retrieve(self.mock_request, pk=self.patient.pk).content
        expected = json_response(self.patient.to_dict(None)).content
        self.assertEqual(expected, response)

    def test_stores_access_log(self):
        self.assertEqual(0, models.PatientRecordAccess.objects.count())
        response = api.PatientViewSet().retrieve(self.mock_request, pk=self.patient.pk).content
        self.assertEqual(1, models.PatientRecordAccess.objects.count())


class PatientRecordAccessViewSetTestCase(OpalTestCase):

    def test_retrieve(self):
        patient = models.Patient.objects.create()
        mock_request = MagicMock(name='request')
        mock_request.user = self.user
        models.PatientRecordAccess.objects.create(patient=patient, user=self.user)
        response = api.PatientRecordAccessViewSet().retrieve(mock_request, pk=patient.pk).content
        loaded = json.loads(response.decode('UTF-8'))
        self.assertEqual(patient.id, loaded[0]['patient'])
        self.assertEqual(self.user.username, loaded[0]['username'])


class PatientListTestCase(TestCase):

    def setUp(self):
        self.mock_request = MagicMock(name='request')

    @patch('opal.core.api.PatientList')
    def test_retrieve_episodes(self, patient_list):
        instantiated_list = patient_list.get.return_value.return_value
        instantiated_list.to_dict.return_value = {}
        expected = json_response({}).content
        response = api.PatientListViewSet().retrieve(self.mock_request, pk='mylist').content
        self.assertEqual(expected, response)

    def test_retrieve_episodes_not_found(self):
        response = api.PatientListViewSet().retrieve(self.mock_request, pk='not a real list at all')
        self.assertEqual(404, response.status_code)


class RegisterTestCase(OpalTestCase):

    @patch('opal.core.api.plugins.OpalPlugin.list')
    def test_register_plugins(self, plugins):
        mock_plugin = MagicMock(name='Mock Plugin')
        mock_plugin.get_apis.return_value = [('thingapi', None)]
        plugins.return_value = [mock_plugin]
        with patch.object(api.router, 'register') as register:
            api.register_plugin_apis()
            register.assert_called_with('thingapi', None)

    @patch("opal.core.api.router.register")
    @patch("opal.core.api.subrecords")
    def test_register_subrecords(self, subrecords, register):
        subrecords.return_value = [HatWearer]
        api.register_subrecords()
        self.assertEqual(register.call_count, 1)
        self.assertTrue(register.call_args[0][0][0], HatWearer.get_api_name())

    @patch("opal.core.api.router.register")
    @patch('opal.core.api.plugins.OpalPlugin.list')
    def test_register_plugin_order(self, plugins, register):
        # plugins should be registered first
        mock_plugin = MagicMock(name='Mock Plugin')
        mock_plugin.get_apis.return_value = [('thingapi', None)]
        plugins.return_value = [mock_plugin]
        api.initialize_router()
        call_args_list = register.call_args_list
        self.assertEqual(
            register.call_args_list[0][0][0], "thingapi"
        )
