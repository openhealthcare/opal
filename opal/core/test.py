"""
OPAL Test base classes
"""
import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils.functional import cached_property

from opal.core.views import OpalSerializer
from opal.models import UserProfile, Patient


class OpalTestCase(TestCase):
    USERNAME = "testuser"
    PASSWORD = "password"

    @cached_property
    def rf(self):
        return RequestFactory()

    @cached_property
    def user(self):
        user = User.objects.create(
            username=self.USERNAME,
            is_staff=True,
            is_superuser=True
        )
        user.set_password(self.PASSWORD)
        user.save()
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            can_extract=True
        )
        return user


    def post_json(self, path, data):
        json_data = json.dumps(data, cls=OpalSerializer)
        return self.client.post(
            path, content_type='application/json', data=json_data
        )

    def put_json(self, path, data):
        json_data = json.dumps(data, cls=OpalSerializer)
        return self.client.put(path, content_type='application/json', data=json_data)

    def assertStatusCode(
            self, path, expected_status_code, follow=True, msg=None
    ):
        response = self.client.get(path, follow=follow)
        self.assertEqual(expected_status_code, response.status_code, msg)

    def new_patient_and_episode_please(self):
        patient = Patient.objects.create()
        episode = patient.create_episode()
        return patient, episode
