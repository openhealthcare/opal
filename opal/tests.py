"""
Unit tests for OPAL.
"""
import datetime
import json

from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models as djangomodels
from django.test import TestCase

from opal.models import Patient, Episode, EpisodeSubrecord, UpdatesFromDictMixin

class UpdatesFromDictMixinTest(TestCase):
    class TestDiagnosis(UpdatesFromDictMixin, djangomodels.Model):
        condition = djangomodels.CharField(max_length=255, blank=True, null=True)
        provisional = djangomodels.BooleanField()
        details = djangomodels.CharField(max_length=255, blank=True)
        date_of_diagnosis = djangomodels.DateField(blank=True, null=True)

    def test_get_fieldnames_to_serialise(self):
        names = self.TestDiagnosis._get_fieldnames_to_serialize()
        expected = ['id', 'condition', 'provisional', 'details', 'date_of_diagnosis']
        self.assertEqual(expected, names)


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

    def test_cannot_create_episode_if_has_active_episode(self):
        episode = self.patient.create_episode()
        episode.set_tag_names(['microbiology'], None)
        with self.assertRaises(Exception):
            self.patient.create_episode()


class EpisodeTest(TestCase):
    fixtures = ['patients_users', 'patients_records', 'patients_options']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.patient = Patient.objects.create()
        self.episode = self.patient.create_episode()

    def test_unicode(self):
        self.assertEqual(' |  | None', self.episode.__unicode__())

    def test_location_subrecord_created(self):
        self.assertEqual(1, self.episode.location_set.count())

    def test_can_set_tag_names(self):
        for tag_names in [
            ['microbiology', 'mine'],
            ['microbiology', 'hiv'],
            ['hiv', 'mine'],
            ]:
            self.episode.set_tag_names(tag_names, self.user)
            self.assertEqual(set(tag_names),
                             set(self.episode.get_tag_names(self.user)))

    def test_user_cannot_see_other_users_mine_tag(self):
        other_user = User.objects.get(pk=2)

        self.episode.set_tag_names(['hiv', 'mine'], self.user)
        self.assertEqual(['hiv'], self.episode.get_tag_names(other_user))

    def test_active_if_tagged_by_non_mine_tag(self):
        self.episode.set_tag_names(['microbiology'], self.user)
        self.assertTrue(self.episode.is_active())

    def test_inactive_if_only_tagged_by_mine_tag(self):
        self.episode.set_tag_names(['mine'], self.user)
        self.assertFalse(self.episode.is_active())

    def test_to_dict(self):
        # TODO: Decouple this from the elCID implementation/move to elCID
        self.maxDiff = None
        expected_data = {
            'id': self.episode.id,
            'prev_episodes': [
                ],
            'next_episodes': [],
            'opat_outstanding_issues': [],
            'opat_review': [],
            'active': False,
            'allergies': [],
            'appointment': [],
            'date_of_admission': None,
            'discharge_date': None,
            'consistency_token': '',
            'demographics': [{
                    u'id': self.patient.demographics_set.get().id,
                    'patient_id': self.patient.id,
                    'consistency_token': '',
                    'date_of_birth': None,
                    'country_of_birth': '',
                    'country_of_birth_fk_id': None,
                    'country_of_birth_ft': '',
                    'ethnicity': None,
                    'hospital_number': '',
                    'nhs_number': None,
                    'name': u'',
                    }],
            'contact_details': [{'address_line1': None,
                                 'address_line2': None,
                                 'city': u'',
                                 'consistency_token': u'',
                                 'county': None,
                                 u'id': 2,
                                 'patient_id': 2,
                                 'post_code': None,
                                 'tel1': None,
                                 'tel2': None}],

            'location': [{
                    u'id': self.episode.location_set.get().id,
                    'episode_id': self.episode.id,
                    'bed': u'',
                    'category': u'',
                    'consistency_token': u'',
                    'hospital': u'',
                    'ward': u'',
                    'opat_discharge': None,
                    'opat_referral': None,
                    'opat_referral_route': None,
                    'opat_referral_team': None,
                    'opat_referral_team_address': None,


                    }],
            'diagnosis': [],
            'past_medical_history': [],
            'general_note': [],
            'opat_line_assessment': [],
            'travel': [],
            'antimicrobial': [],
            'carers': [{'consistency_token': u'',
                        'gp_id': None,
                        u'id': 2,
                        'nurse_id': None,
                        'patient_id': 2}],
            'line': [],
            'microbiology_input': [],
            'todo': [],
            'tagging': [{}],
            'microbiology_test': [],
            }
        self.assertEqual(expected_data, self.episode.to_dict(self.user))

    def test_to_dict_with_multiple_episodes(self):
        episode = Episode.objects.get(pk=1)
        serialised = episode.to_dict(self.user)
        self.assertEqual(1, len(serialised['prev_episodes']))
        self.assertEqual(datetime.date(2012, 7, 25),
                         serialised['prev_episodes'][0]['date_of_admission'])

    def test_to_dict_episode_ordering(self):
        episode = Episode.objects.get(pk=1)
        patient = episode.patient
        admitted = datetime.date(2011, 7, 25)
        new_episode = Episode(patient=patient, date_of_admission=admitted)
        new_episode.save()

        serialised = episode.to_dict(self.user)
        self.assertEqual(2, len(serialised['prev_episodes']))
        self.assertEqual(datetime.date(2011, 7, 25),
                         serialised['prev_episodes'][0]['date_of_admission'])
        self.assertEqual(datetime.date(2012, 7, 25),
                         serialised['prev_episodes'][1]['date_of_admission'])



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
