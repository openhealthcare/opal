"""
Opal Testing utilities
"""
import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils.functional import cached_property

from opal.core.serialization import OpalSerializer
from opal.models import UserProfile, Patient


class OpalTestCase(TestCase):
    USERNAME = "testuser"
    PASSWORD = "password"

    @cached_property
    def rf(self):
        return RequestFactory()

    def make_user(self, password, **kwargs):
        user = User.objects.create(**kwargs)
        user.set_password(password)
        user.save()
        return user

    @cached_property
    def user(self):
        user = self.make_user(
            self.PASSWORD,
            username=self.USERNAME,
            is_staff=True,
            is_superuser=True
        )
        profile = UserProfile.objects.get(
            user=user,
        )
        if not profile.can_extract:
            profile.can_extract = True
            profile.save()
        return user

    def post_json(self, path, data):
        json_data = json.dumps(data, cls=OpalSerializer)
        return self.client.post(
            path, content_type='application/json', data=json_data
        )

    def put_json(self, path, data):
        json_data = json.dumps(data, cls=OpalSerializer)
        return self.client.put(path,
                               content_type='application/json',
                               data=json_data)

    def assertStatusCode(
            self, path, expected_status_code, follow=True, msg=None
    ):
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.get(path, follow=follow)
        self.assertEqual(expected_status_code, response.status_code, msg)

    def new_patient_and_episode_please(self):
        patient = Patient.objects.create()
        episode = patient.create_episode()
        return patient, episode
