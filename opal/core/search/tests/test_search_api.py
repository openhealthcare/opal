from mock import patch

from rest_framework.reverse import reverse
from rest_framework import status

from opal.core.search import api
from opal.core.test import OpalTestCase
from opal.tests.models import HatWearer


class ExtractSchemaTestCase(OpalTestCase):

    @patch('opal.core.search.api.schemas')
    def test_records(self, schemas):
        schemas.extract_search_schema.return_value = [{}]
        self.assertEqual([{}], api.ExtractSchemaViewSet().list(None).data)

    def test_integration_records(self):
        self.assertTrue(api.ExtractSchemaViewSet().list(None).data)


class DataDictionaryTestCase(OpalTestCase):
    @patch('opal.core.search.api.ExtractCsvSerialiser')
    def test_records(self, serialiser):
        serialiser.get_data_dictionary_schema.return_value = [{}]
        self.assertEqual([{}], api.DataDictionaryViewSet().list(None).data)

    def test_integration_records(self):
        self.assertTrue(api.DataDictionaryViewSet().list(None).data)


class LoginRequredTestCase(OpalTestCase):
    """
        we expect almost all views to 401
    """
    def setUp(self):
        self.patient, self.episode = self.new_patient_and_episode_please()
        self.request = self.rf.get("/")
        self.hat_wearer = HatWearer.objects.create(episode=self.episode)

    def get_urls(self):
        return [
            reverse('extract-schema-list', request=self.request),
            reverse('data-dictionary-list', request=self.request),
        ]

    def test_403(self):
        for url in self.get_urls():
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN
            )
