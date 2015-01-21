"""
Unit tests for OPAL.
"""
import datetime
import json

from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models as djangomodels
from django.test import TestCase

from opal.models import (Patient, Episode, EpisodeSubrecord,
                         UpdatesFromDictMixin, Macro)

from updates_from_dict import *
from macro import *
from templatetags_forms import *
from episode_tests import *
from user_profile import *
from utils_fields import *

"""
Models
"""
class PatientTest(TestCase):
    fixtures = ['patients_users', 'patients_records', 'patients_options']
    maxDiff = None

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.patient = Patient.objects.create()

    def test_demographics_subrecord_created(self):
        self.assertEqual(1, self.patient.demographics_set.count())

    def test_can_create_episode(self):
        episode = self.patient.create_episode()
        self.assertEqual(Episode, type(episode))

    def test_get_active_episode(self):
        episode1 = self.patient.create_episode()
        episode2 = self.patient.create_episode()
        episode2.set_tag_names(['microbiology'], None)
        self.assertEqual(episode2.id, self.patient.get_active_episode().id)

    def test_get_active_episode_with_no_episodes(self):
        self.assertIsNone(self.patient.get_active_episode())

    def test_get_active_episode_with_no_active_episodes(self):
        self.patient.create_episode()
        self.patient.create_episode()
        self.assertIsNone(self.patient.get_active_episode())

"""
Views
"""
class EpisodeDetailViewTest(TestCase):
    fixtures = ['patients_users', 'patients_options', 'patients_records']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.assertTrue(self.client.login(username=self.user.username,
                                          password='password'))
        self.patient = Patient.objects.get(pk=1)
        self.episode = self.patient.episode_set.all()[0]

    def post_json(self, path, data):
        json_data = json.dumps(data, cls=DjangoJSONEncoder)
        return self.client.post(path, content_type='application/json', data=json_data)

    def put_json(self, path, data):
        json_data = json.dumps(data, cls=DjangoJSONEncoder)
        return self.client.put(path, content_type='application/json', data=json_data)

    def test_update_nonexistent_episode(self):
        data = {
            'consistency_token': '456456',
            'id': 4561325,
            }
        response = self.put_json('/episode/4561325', data)
        self.assertEqual(404, response.status_code)

    def test_update_episode(self):
        episode = self.patient.episode_set.all()[0]
        today = datetime.date.today()
        data = episode.to_dict(self.user, shallow=True)
        data['discharge_date'] = today
        self.assertNotEqual(episode.discharge_date, today)
        response = self.put_json('/episode/{0}'.format(episode.id), data)

        self.assertEqual(200, response.status_code)
        episode = self.patient.episode_set.all()[0]
        self.assertEqual(episode.discharge_date, today)

class ListSchemaViewTest(TestCase):
    fixtures = ['patients_users', 'patients_options', 'patients_records']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.assertTrue(self.client.login(username=self.user.username,
                                          password='password'))
        self.patient = Patient.objects.get(pk=1)

    def assertStatusCode(self, path, expected_status_code):
        response = self.client.get(path)
        self.assertEqual(expected_status_code, response.status_code)

    def test_list_schema_view(self):
        self.assertStatusCode('/schema/list/', 200)

