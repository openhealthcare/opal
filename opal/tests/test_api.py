"""
Tests for the OPAL API
"""
import json
from datetime import date, timedelta
from django.utils import timezone

from django.contrib.auth.models import User
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from mock import patch, MagicMock

from opal import models
from opal.tests.models import Colour, PatientColour, HatWearer, Hat
from opal.core.test import OpalTestCase
from opal.core.views import _build_json_response

# this is used just to import the class for
# EpisodeListApiTestCase and OptionsViewSetTestCase
from opal.tests.test_patient_lists import TaggingTestPatientList # flake8: noqa

from opal.core import api


class OPALRouterTestCase(TestCase):
    def test_default_base_name(self):
        class ViewSet:
            base_name = 'the name'
        self.assertEqual(api.OPALRouter().get_default_base_name(ViewSet), 'the name')


class RecordTestCase(TestCase):

    @patch('opal.core.api.schemas')
    def test_records(self, schemas):
        schemas.list_records.return_value = [{}]
        self.assertEqual([{}], api.RecordViewSet().list(None).data)


class EpisodeListApiTestCase(OpalTestCase):
    def test_episode_list_view(self):
        request = MagicMock(name='mock request')
        request.user = self.user
        view = api.EpisodeListApi()
        view.request = request
        resp = view.get(tag="eater", subtag="herbivore")
        self.assertEqual(200, resp.status_code)


class ExtractSchemaTestCase(TestCase):

    @patch('opal.core.api.schemas')
    def test_records(self, schemas):
        schemas.extract_schema.return_value = [{}]
        self.assertEqual([{}], api.ExtractSchemaViewSet().list(None).data)


class OptionTestCase(TestCase):
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
        request = mock_request
        self.request = request
        self.viewset = api.OptionsViewSet()
        self.viewset.request = mock_request
        self.response = self.viewset.list(request)

    def test_options_loader(self):
        result = self.response.data
        self.assertIn("hat", result)
        self.assertEqual(set(result["hat"]), {"top", "bowler", "high"})
        self.assertEqual(self.response.status_code, 200)

    def test_first_list_slug(self):
        result = self.response.data
        self.assertEqual('carnivore', result['first_list_slug'])

    def test_first_list_slug_no_lists(self):
        def nongen():
            for x in range(0, 0):
                yield x

        with patch.object(api.PatientList, 'for_user') as for_user:
            for_user.return_value = nongen()
            result = self.viewset.list(self.request).data
            self.assertEqual('', result['first_list_slug'])

    def test_tag_display(self):
        result = self.response.data
        self.assertEqual('Herbivores', result['tag_display']['herbivore'])

    def test_tag_visible_in_list(self):
        result = self.response.data
        self.assertIn('carnivore', result['tag_visible_in_list'])

    def test_tag_direct_add(self):
        result = self.response.data
        # .direct_add = False
        self.assertNotIn('carnivore', result['tag_direct_add'])
        # .direct_add = default
        self.assertIn('herbivore', result['tag_direct_add'])

    def test_tag_slug(self):
        result = self.response.data
        self.assertEqual('eater-herbivore', result['tag_slugs']['herbivore'])

    def test_tags(self):
        result = self.response.data

        expected = {
            "carnivore": {
                'direct_add': False,
                'display_name': 'Carnivores',
                'slug': 'carnivore',
                'name': 'carnivore'
            },
            "herbivore": {
                'direct_add': True,
                'display_name': 'Herbivores',
                'slug': 'eater-herbivore',
                'name': 'herbivore',
                'parent_tag': 'eater'
            },
              'omnivore': {
                'direct_add': True,
                'display_name': 'Omnivore',
                'name': 'omnivore',
                'slug': 'eater-omnivore',
                'parent_tag': 'eater'
            },
              'mine': {
                'direct_add': True,
                'display_name': 'Mine',
                'name': 'mine',
                'slug': 'mine'
            }
        }

        self.assertEqual(expected, result['tags'])


class SubrecordTestCase(TestCase):

    def setUp(self):
        self.patient = models.Patient.objects.create()
        self.episode = models.Episode.objects.create(patient=self.patient)
        self.user = User.objects.create(username='testuser')

        class OurViewSet(api.SubrecordViewSet):
            base_name = 'colour'
            model     = Colour

        class OurPatientViewSet(api.SubrecordViewSet):
            base_name = 'patientcolour'
            model = PatientColour

        self.model = Colour
        self.viewset = OurViewSet
        self.patientviewset = OurPatientViewSet

    def test_retrieve(self):
        with patch.object(self.model.objects, 'get') as mockget:
            mockget.return_value.to_dict.return_value = 'serialized colour'

            response = self.viewset().retrieve(MagicMock(name='request'), pk=1)
            self.assertEqual('serialized colour', response.data)

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
        self.assertEqual('blue', json.loads(response.content)['name'])

    def test_create_patient_subrecord(self):
        mock_request = MagicMock(name='mock request')
        mock_request.user = self.user
        mock_request.data = {'name': 'blue', 'episode_id': self.episode.pk,
                             'patient_id': self.patient.pk}
        response = self.patientviewset().create(mock_request)
        self.assertEqual('blue', json.loads(response.content)['name'])

    def test_create_nonexistant_episode(self):
        mock_request = MagicMock(name='mock request')
        mock_request.data = {'name': 'blue', 'episode_id': 56785}
        mock_request.user = self.user
        response = self.viewset().create(mock_request)
        self.assertEqual(400, response.status_code)

    def test_create_unexpected_field(self):
        mock_request = MagicMock(name='mock request')
        mock_request.data = {'name': 'blue', 'hue': 'enabled', 'episode_id': self.episode.pk}
        mock_request.user = self.user
        response = self.viewset().create(mock_request)
        self.assertEqual(400, response.status_code)

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
        self.assertEqual('green', json.loads(response.content)['name'])

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
        hw = HatWearer.objects.get(name="Jane")
        hat_names = hw.hats.all().values_list("name", flat=True)
        self.assertEqual(list(hat_names), [unicode(self.bowler.name)])


class UserProfileTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='testuser')
        models.UserProfile.objects.create(user=self.user)
        self.mock_request = MagicMock(name='request')
        self.mock_request.user = self.user

    def test_user_profile(self):
        with patch.object(self.user, 'is_authenticated', return_value=True):
            response = api.UserProfileViewSet().list(self.mock_request)
            expected = {
                'readonly'   : False,
                'can_extract': False,
                'filters'    : [],
                'roles'      : {'default': []}
            }
            self.assertEqual(expected, response.data)

    def test_user_profile_readonly(self):
        with patch.object(self.user, 'is_authenticated', return_value=True):
            profile = self.user.profile
            profile.readonly = True
            profile.save()
            response = api.UserProfileViewSet().list(self.mock_request)
            self.assertEqual(True, response.data['readonly'])

    def test_user_profile_not_logged_in(self):
        mock_request = MagicMock(name='request')
        mock_request.user.is_authenticated.return_value = False
        response = api.UserProfileViewSet().list(mock_request)
        self.assertEqual(401, response.status_code)




class TaggingTestCase(TestCase):

    def setUp(self):
        self.patient = models.Patient.objects.create()
        self.episode = models.Episode.objects.create(patient=self.patient)
        self.user    = User.objects.create(username='testuser')
        self.micro   = models.Team.objects.create(name='micro', title='microbiology')
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

    def test_untag_episode(self):
        self.assertEqual(list(self.episode.get_tag_names(self.user)), [])
        self.episode.set_tag_names(['micro'], self.user)
        self.mock_request.data = {'micro': False}
        response = api.TaggingViewSet().update(self.mock_request, pk=self.episode.pk)
        self.assertEqual(202, response.status_code)
        self.assertEqual(list(self.episode.get_tag_names(self.user)), [])

    def test_tag_nonexistent_episode(self):
        response = api.TaggingViewSet().update(self.mock_request, pk=56576)
        self.assertEqual(404, response.status_code)


class EpisodeTestCase(TestCase):
    def setUp(self):
        self.patient = models.Patient.objects.create()
        self.demographics = self.patient.demographics_set.get()
        self.episode = models.Episode.objects.create(patient=self.patient)
        self.user = User.objects.create(username='testuser')
        self.mock_request = MagicMock(name='request')
        self.mock_request.user = self.user
        self.mock_request.query_params = {}

    def test_retrieve_episode(self):
        response = api.EpisodeViewSet().retrieve(self.mock_request, pk=self.episode.pk).data
        expected = json.loads(_build_json_response(self.episode.to_dict(self.user)).content)
        self.assertEqual(expected, response)

    def test_retrieve_nonexistent_episode(self):
        response = api.EpisodeViewSet().retrieve(self.mock_request, pk=678687)
        self.assertEqual(404, response.status_code)

    def test_list(self):
        response = api.EpisodeViewSet().list(self.mock_request)
        expected = [self.episode.to_dict(self.user)]
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, response.data)

    def test_list_unauthenticated(self):
        pass #TODO TEST THIS

    def test_create_existing_patient(self):
        self.demographics.name = 'Aretha Franklin'
        self.demographics.hospital_number = '123123123'
        self.demographics.save()
        self.mock_request.data = {
            "tagging"          :[ { "micro":True }],
            "date_of_admission": "14/01/2015",
            "demographics"     : {
                "hospital_number": self.demographics.hospital_number
            }
        }
        response = api.EpisodeViewSet().create(self.mock_request)
        self.assertEqual(201, response.status_code)
        self.assertEqual(2, self.patient.episode_set.count())
        self.assertEqual(date(2015, 1, 14), response.data['date_of_admission'])

    def test_create_new_patient(self):
        pcount = models.Patient.objects.filter(
            demographics__hospital_number="999000999").count()
        self.assertEqual(0, pcount)
        self.mock_request.data = {
            "tagging"           :[ { "micro":True }],
            "date_of_admission" : "14/01/2015",
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

        self.assertEqual(201, response.status_code)
        pcount = models.Patient.objects.filter(
            demographics__hospital_number="999000999").count()
        self.assertEqual(1, pcount)

    def test_create_sets_demographics(self):
        pcount = models.Patient.objects.filter(
            demographics__hospital_number="9999000999").count()
        self.assertEqual(0, pcount)
        self.mock_request.data = {
            "tagging"                :[ { "micro":True }],
            "date_of_admission"      : "14/01/2015",
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
        demographics = patient.demographics_set.get()
        self.assertEqual("Alain", demographics.first_name)
        self.assertEqual("Anderson", demographics.surname)
        self.assertEqual("Male", demographics.sex)

    def test_create_sets_location(self):
        pcount = models.Patient.objects.filter(
            demographics__hospital_number="9999000999").count()
        self.assertEqual(0, pcount)
        self.mock_request.data = {
            "tagging"                :[ { "micro":True }],
            "date_of_admission"      : "14/01/2015",
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
        pass

    def test_update(self):
        pass

    def test_update_nonexistent(self):
        pass



class PatientTestCase(OpalTestCase):
    def setUp(self):
        self.patient      = models.Patient.objects.create()
        self.mock_request = MagicMock(name='request')
        self.mock_request.user = self.user

    def test_retrieve_patient(self):
        response = api.PatientViewSet().retrieve(self.mock_request, pk=self.patient.pk).content
        expected = _build_json_response(self.patient.to_dict(None)).content
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
        loaded = json.loads(response)
        self.assertEqual(patient.id, loaded[0]['patient'])
        self.assertEqual(self.user.username, loaded[0]['username'])


class PatientListTestCase(TestCase):

    def setUp(self):
        self.mock_request = MagicMock(name='request')

    @patch('opal.core.api.PatientList')
    def test_retrieve_episodes(self, patient_list):
        instantiated_list = patient_list.get.return_value.return_value
        instantiated_list.to_dict.return_value = {}
        expected = _build_json_response({}).content
        response = api.PatientListViewSet().retrieve(self.mock_request, pk='mylist').content
        self.assertEqual(expected, response)

    def test_retrieve_episodes_not_found(self):
        response = api.PatientListViewSet().retrieve(self.mock_request, pk='not a real list at all')
        self.assertEqual(404, response.status_code)
