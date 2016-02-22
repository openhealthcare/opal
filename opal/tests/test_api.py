"""
Tests for the OPAL API
"""
from datetime import date, timedelta
from django.utils import timezone

from django.contrib.auth.models import User
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from mock import patch, MagicMock

from opal import models
from opal.tests.models import Colour, PatientColour, HatWearer, Hat

from opal.core import api


class OPALRouterTestCase(TestCase):
    def test_default_base_name(self):
        class ViewSet:
            base_name = 'the name'
        self.assertEqual(api.OPALRouter().get_default_base_name(ViewSet), 'the name')


class FlowTestCase(TestCase):

    @patch('opal.core.api.app')
    def test_list(self, app):
        app.flows.return_value = [{}]
        self.assertEqual([{}], api.FlowViewSet().list(None).data)


class RecordTestCase(TestCase):

    @patch('opal.core.api.schemas')
    def test_records(self, schemas):
        schemas.list_records.return_value = [{}]
        self.assertEqual([{}], api.RecordViewSet().list(None).data)


class ListSchemaTestCase(TestCase):

    @patch('opal.core.api.schemas')
    def test_records(self, schemas):
        schemas.list_schemas.return_value = [{}]
        self.assertEqual([{}], api.ListSchemaViewSet().list(None).data)


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
        self.viewset = api.OptionsViewSet

    def test_options_loader(self):
        mock_request = MagicMock(name='mock request')
        mock_request.user = self.user
        response = self.viewset().list(mock_request)
        result = response.data
        self.assertIn("hat", result)
        self.assertEqual(set(result["hat"]), {"top", "bowler", "high"})
        self.assertEqual(response.status_code, 200)


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
        self.assertEqual('blue', response.data['name'])

    def test_create_patient_subrecord(self):
        mock_request = MagicMock(name='mock request')
        mock_request.user = self.user
        mock_request.data = {'name': 'blue', 'episode_id': self.episode.pk,
                             'patient_id': self.patient.pk}
        response = self.patientviewset().create(mock_request)
        self.assertEqual('blue', response.data['name'])

    @patch('opal.core.api.glossolalia.change')
    def test_create_pings_integration(self, change):
        mock_request = MagicMock(name='mock request')
        mock_request.data = {'name': 'blue', 'episode_id': self.episode.pk}
        mock_request.user = self.user
        response = self.viewset().create(mock_request)
        self.assertEqual(1, change.call_count)

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
        self.assertEqual('green', response.data['name'])

    @patch('opal.core.api.glossolalia.change')
    def test_update_pings_integration(self, change):
        colour = Colour.objects.create(name='blue', episode=self.episode)
        mock_request = MagicMock(name='mock request')
        mock_request.data = {
            'name'             : 'green',
            'episode_id'       : self.episode.pk,
            'id'               : colour.pk,
            'consistency_token': colour.consistency_token
        }
        mock_request.user = self.user
        response = self.viewset().update(mock_request, pk=colour.pk)
        self.assertEqual(202, response.status_code)
        self.assertEqual(1, change.call_count)

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

    @patch('opal.core.api.glossolalia.change')
    def test_delete_pings_integration(self, change):
        colour = Colour.objects.create(episode=self.episode)
        mock_request = MagicMock(name='mock request')
        mock_request.user = self.user
        response = self.viewset().destroy(mock_request, pk=colour.pk)
        self.assertEqual(202, response.status_code)
        self.assertEqual(1, change.call_count)


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


    @patch('opal.core.api.glossolalia.transfer')
    def test_tagging_pings_integration(self, transfer):
        self.assertEqual(list(self.episode.get_tag_names(self.user)), [])
        self.mock_request.data = {'micro': True}
        response = api.TaggingViewSet().update(self.mock_request, pk=self.episode.pk)
        self.assertEqual(202, response.status_code)
        self.assertEqual(1, transfer.call_count)

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
        self.micro = models.Team.objects.create(name='micro', title='microbiology')
        self.ortho = models.Team.objects.create(
            name='micro_ortho', title='Micro Ortho',
            parent=self.micro)

    def test_retrieve_episode(self):
        response = api.EpisodeViewSet().retrieve(self.mock_request, pk=self.episode.pk)
        self.assertEqual(self.episode.to_dict(self.user), response.data)

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

    def test_list_for_tag_empty(self):
        self.mock_request.query_params = {'tag': 'micro'}
        response = api.EpisodeViewSet().list(self.mock_request)
        self.assertEqual(200, response.status_code)
        self.assertEqual([], response.data)

    def test_list_for_tag(self):
        self.mock_request.query_params = {'tag': 'micro'}
        self.episode.set_tag_names(['micro'], self.user)
        expected = models.Episode.objects.serialised(self.user, [self.episode])
        response = api.EpisodeViewSet().list(self.mock_request)
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, response.data)

    def test_list_for_subtag_empty(self):
        self.mock_request.query_params = {'tag': 'micro', 'subtag': 'micro_ortho'}
        response = api.EpisodeViewSet().list(self.mock_request)
        self.assertEqual(200, response.status_code)
        self.assertEqual([], response.data)

    def test_list_for_subtag(self):
        self.mock_request.query_params = {'tag': 'micro', 'subtag': 'micro_ortho'}
        self.episode.set_tag_names(['micro_ortho'], self.user)
        expected = models.Episode.objects.serialised(self.user, [self.episode])
        response = api.EpisodeViewSet().list(self.mock_request)
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, response.data)

    def test_create_existing_patient(self):
        self.demographics.name = 'Aretha Franklin'
        self.demographics.hospital_number = '123123123'
        self.demographics.save()
        self.mock_request.data = {
            "tagging"                :[ { "micro":True }],
            "date_of_admission"      : "2015-01-14",
            "patient_hospital_number": self.demographics.hospital_number
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
            "tagging"                :[ { "micro":True }],
            "date_of_admission"      : "2015-01-14",
            "patient_hospital_number": "999000999"
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

    @patch('opal.core.api.glossolalia.admit')
    def test_create_pings_integration(self, admit):
        pass

    def test_update(self):
        pass

    def test_update_nonexistent(self):
        pass

    def test_update_pings_integration(self):
        pass


class PatientTestCase(TestCase):
    def setUp(self):
        self.patient      = models.Patient.objects.create()
        self.mock_request = MagicMock(name='request')

    def test_retrieve_episode(self):
        response = api.PatientViewSet().retrieve(self.mock_request, pk=self.patient.pk)
        self.assertEqual(self.patient.to_dict(None), response.data)
