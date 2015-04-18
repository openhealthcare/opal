"""
Tests for the OPAL API
"""
from django.contrib.auth.models import User
from django.test import TestCase
from mock import patch, MagicMock

from opal import models
from opal.tests.models import Colour

from opal.views import api

class OPALRouterTestCase(TestCase):
    def test_default_base_name(self):
        class ViewSet:
            base_name = 'the name'
        self.assertEqual(api.OPALRouter().get_default_base_name(ViewSet), 'the name')


class FlowTestCase(TestCase):

    @patch('opal.views.api.app')
    def test_list(self, app):
        app.flows.return_value = [{}]
        self.assertEqual([{}], api.FlowViewSet().list(None).data)
        
        
class RecordTestCase(TestCase):
    
    @patch('opal.views.api.schemas')
    def test_records(self, schemas):
        schemas.list_records.return_value = [{}]
        self.assertEqual([{}], api.RecordViewSet().list(None).data)


class ListSchemaTestCase(TestCase):
    
    @patch('opal.views.api.schemas')
    def test_records(self, schemas):
        schemas.list_schemas.return_value = [{}]
        self.assertEqual([{}], api.ListSchemaViewSet().list(None).data)


class ExtractSchemaTestCase(TestCase):
    
    @patch('opal.views.api.schemas')
    def test_records(self, schemas):
        schemas.extract_schema.return_value = [{}]
        self.assertEqual([{}], api.ExtractSchemaViewSet().list(None).data)


class SubrecordTestCase(TestCase):
    
    def setUp(self):
        self.patient = models.Patient.objects.create()
        self.episode = models.Episode.objects.create(patient=self.patient)
        self.user    = User.objects.create(username='testuser')
        
        class OurViewSet(api.SubrecordViewSet):
            base_name = 'colour'
            model     = Colour

        self.model   = Colour
        self.viewset = OurViewSet

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
        self.assertEqual('blue', response.data['colour'][0]['name'])
        self.assertEqual(self.episode.pk, response.data['id'])

    @patch('opal.views.api.glossolalia.change')
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

