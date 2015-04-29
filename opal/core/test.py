"""
OPAL Test base classes
"""
import json 

from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase

class OpalTestCase(TestCase):

    def post_json(self, path, data):
        json_data = json.dumps(data, cls=DjangoJSONEncoder)
        return self.client.post(path, content_type='application/json', data=json_data)

    def put_json(self, path, data):
        json_data = json.dumps(data, cls=DjangoJSONEncoder)
        return self.client.put(path, content_type='application/json', data=json_data)
    
    def assertStatusCode(self, path, expected_status_code):
        response = self.client.get(path)
        self.assertEqual(expected_status_code, response.status_code)

