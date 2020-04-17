from opal.core.test import OpalTestCase
from unittest.mock import patch
from opal.core.search import api
from rest_framework.reverse import reverse
from rest_framework import status


class ExtractSchemaTestCase(OpalTestCase):

    @patch('opal.core.search.api.schemas')
    def test_records(self, schemas):
        schemas.extract_schema.return_value = [{}]
        self.assertEqual([{}], api.ExtractSchemaViewSet().list(None).data)


class LoginRequredTestCase(OpalTestCase):
    """
        we expect almost all views to 401
    """
    def setUp(self):
        self.patient, self.episode = self.new_patient_and_episode_please()
        self.request = self.rf.get("/")

    def test_401(self):
        url = reverse('extract-schema-list', request=self.request)
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            401
        )
