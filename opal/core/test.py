"""
OPAL Test base classes
"""
import json

from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase
from django.test.client import RequestFactory

from opal.models import UserProfile


class OpalTestCase(TestCase):
    USERNAME = "testuser"
    PASSWORD = "password"

    def __init__(self, *a, **k):
        self.rf = RequestFactory()
        self._user = None
        super(OpalTestCase, self).__init__(*a, **k)

    @property
    def user(self):
        if self._user is None:
            self._user = User.objects.create(
                username=self.USERNAME,
                is_staff=True,
                is_superuser=True
            )
            self._user.set_password(self.PASSWORD)
            self._user.save()
            profile, _ = UserProfile.objects.get_or_create(
                user=self.user,
                can_extract=True
            )
        return self._user

    def post_json(self, path, data):
        json_data = json.dumps(data, cls=DjangoJSONEncoder)
        return self.client.post(
            path, content_type='application/json', data=json_data
        )

    def put_json(self, path, data):
        json_data = json.dumps(data, cls=DjangoJSONEncoder)
        return self.client.put(path, content_type='application/json', data=json_data)

    def assertStatusCode(self, path, expected_status_code):
        response = self.client.get(path)
        self.assertEqual(expected_status_code, response.status_code)
