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
                         UpdatesFromDictMixin, Macro, Team)

from updates_from_dict import *
from macro import *
from templatetags_forms import *
from episode_tests import *
from user_profile import *
from utils_fields import *
from opal.tests.test_api import *

"""
Models
"""
class PatientTest(TestCase):
    fixtures = ['patients_users', 'patients_records', 'patients_options']
    maxDiff = None

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.patient = Patient.objects.create()
        self.micro   = Team.objects.create(name='microbiology', title='Microbiology')

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

