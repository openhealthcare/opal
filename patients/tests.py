import datetime
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase
from django.contrib.auth.models import User
from patients import models
from patients.models import Patient, Episode
from patients import exceptions


class PatientTest(TestCase):
    fixtures = ['patients_users', 'patients_records']

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

    def test_to_dict(self):
        expected_data = {
            'id': self.patient.id,
            'episodes': [],
        }
        self.assertEqual(expected_data, self.patient.to_dict(self.user))


class EpisodeTest(TestCase):
    fixtures = ['patients_users', 'patients_records']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.patient = Patient.objects.create()
        self.episode = self.patient.create_episode()

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
        expected_data = {
            'id': self.episode.id,
            'demographics': [{
                'id': self.patient.demographics_set.get().id,
                'patient_id': self.patient.id,
                'consistency_token': '',
                'date_of_birth': None,
                'hospital_number': '',
                'name': '',
                }],
            'location': [{
                'id': self.episode.location_set.get().id,
                'episode_id': self.episode.id,
                'bed': '',
                'category': '',
                'consistency_token': '',
                'date_of_admission': None,
                'discharge_date': None,
                'hospital': '',
                'tags': {},
                'ward': '',
                }],
            'diagnosis': [],
            'past_medical_history': [],
            'general_note': [],
            'travel': [],
            'antimicrobial': [],
            'microbiology_input': [],
            'todo': [],
            'microbiology_test': [],
        }
        self.assertEqual(expected_data, self.episode.to_dict(self.user))


class DemographicsTest(TestCase):
    fixtures = ['patients_users', 'patients_records']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.patient = models.Patient.objects.get(pk=1)
        self.demographics = self.patient.demographics_set.get()

    def test_to_dict(self):
        expected_data = {
            'consistency_token': '12345678',
            'patient_id': self.patient.id,
            'id': self.demographics.id,
            'name': 'John Smith',
            'date_of_birth': datetime.date(1972, 6, 20),
            'hospital_number': 'AA1111',
        }
        self.assertEqual(expected_data, self.demographics.to_dict(self.user))

    def test_update_from_dict(self):
        data = {
            'consistency_token': '12345678',
            'id': self.demographics.id,
            'name': 'Johann Schmidt',
            'date_of_birth': '1972-6-21',
            'hospital_number': 'AA1112',
        }
        self.demographics.update_from_dict(data, self.user)
        demographics = self.patient.demographics_set.get()

        self.assertEqual('Johann Schmidt', demographics.name)
        self.assertEqual(datetime.date(1972, 6, 21), demographics.date_of_birth)
        self.assertEqual('AA1112', demographics.hospital_number)

    def test_update_from_dict_with_missing_consistency_token(self):
        with self.assertRaises(exceptions.APIError):
            self.demographics.update_from_dict({}, self.user)

    def test_update_from_dict_with_incorrect_consistency_token(self):
        with self.assertRaises(exceptions.ConsistencyError):
            self.demographics.update_from_dict({'consistency_token': '87654321'}, self.user)

    def test_field_schema(self):
        schema = models.Demographics.build_field_schema()
        expected_schema = [
                {'name': 'consistency_token', 'type': 'token'},
                {'name': 'name', 'type': 'string'},
                {'name': 'hospital_number', 'type': 'string'},
                {'name': 'date_of_birth', 'type': 'date'},
        ]
        self.assertEqual(expected_schema, schema)


class LocationTest(TestCase):
    fixtures = ['patients_users', 'patients_records']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.episode = models.Episode.objects.get(pk=1)
        self.location = self.episode.location_set.get()

    def test_to_dict(self):
        expected_data = {
            'consistency_token': '12345678',
            'episode_id': self.episode.id,
            'id': self.location.id,
            'category': 'Inpatient',
            'hospital': 'UCH',
            'ward': 'T10',
            'bed': '13',
            'date_of_admission': datetime.date(2013, 7, 25),
            'discharge_date': None,
            'tags': {'microbiology': True, 'mine': True},
        }
        self.assertEqual(expected_data, self.location.to_dict(self.user))

    def test_update_from_dict(self):
        data = {
            'consistency_token': '12345678',
            'id': self.location.id,
            'category': 'Inpatient',
            'hospital': 'UCH',
            'ward': 'T10',
            'bed': '13',
            'date_of_admission': '2013-7-25',
            'discharge_date':  '2013-8-25',
            'tags': {'microbiology': False, 'mine': True},
        }
        self.location.update_from_dict(data, self.user)
        location = self.episode.location_set.get()

        self.assertEqual(datetime.date(2013, 8, 25), location.discharge_date)
        self.assertEqual({'mine': True}, location.get_tags(self.user))

    def test_field_schema(self):
        schema = models.Location.build_field_schema()
        expected_schema = [
                {'name': 'consistency_token', 'type': 'token'},
                {'name': 'category', 'type': 'string'},
                {'name': 'hospital', 'type': 'string'},
                {'name': 'ward', 'type': 'string'},
                {'name': 'bed', 'type': 'string'},
                {'name': 'date_of_admission', 'type': 'date'},
                {'name': 'discharge_date', 'type': 'date'},
                {'name': 'tags', 'type': 'list'},
        ]
        self.assertEqual(expected_schema, schema)


class DiagnosisTest(TestCase):
    fixtures = ['patients_users', 'patients_records', 'patients_options']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.episode = models.Episode.objects.get(pk=1)
        self.diagnosis = self.episode.diagnosis_set.all()[0]

    def test_to_dict(self):
        expected_data = {
            'consistency_token': '12345678',
            'episode_id': self.episode.id,
            'id': self.diagnosis.id,
            'condition': 'Some condition',
            'provisional': False,
            'details': '',
            'date_of_diagnosis': datetime.date(2013, 7, 25),
        }
        self.assertEqual(expected_data, self.diagnosis.to_dict(self.user))

    def test_update_from_dict_with_existing_condition(self):
        data = {
            'consistency_token': '12345678',
            'id': self.diagnosis.id,
            'condition': 'Some other condition',
        }
        self.diagnosis.update_from_dict(data, self.user)
        diagnosis = self.episode.diagnosis_set.all()[0]
        self.assertEqual('Some other condition', diagnosis.condition)

    def test_update_from_dict_with_synonym_for_condition(self):
        data = {
            'consistency_token': '12345678',
            'id': self.diagnosis.id,
            'condition': 'Condition synonym',
        }
        self.diagnosis.update_from_dict(data, self.user)
        diagnosis = self.episode.diagnosis_set.all()[0]
        self.assertEqual('Some other condition', diagnosis.condition)

    def test_update_from_dict_with_new_condition(self):
        data = {
            'consistency_token': '12345678',
            'id': self.diagnosis.id,
            'condition': 'New condition',
        }
        self.diagnosis.update_from_dict(data, self.user)
        diagnosis = self.episode.diagnosis_set.all()[0]
        self.assertEqual('New condition', diagnosis.condition)
    
    def test_field_schema(self):
        schema = models.Diagnosis.build_field_schema()
        expected_schema = [
                {'name': 'consistency_token', 'type': 'token'},
                {'name': 'provisional', 'type': 'boolean'},
                {'name': 'details', 'type': 'string'},
                {'name': 'date_of_diagnosis', 'type': 'date'},
                {'name': 'condition', 'type': 'string'},
        ]
        self.assertEqual(expected_schema, schema)


class ViewsTest(TestCase):
    fixtures = ['patients_users', 'patients_options', 'patients_records']
    
    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.assertTrue(self.client.login(username=self.user.username, password='password'))
        self.patient = models.Patient.objects.get(pk=1)

    def assertStatusCode(self, path, expected_status_code):
        response = self.client.get(path)
        self.assertEqual(expected_status_code, response.status_code)

    def post_json(self, path, data):
        json_data = json.dumps(data, cls=DjangoJSONEncoder)
        return self.client.post(path, content_type='application/json', data=json_data)

    def put_json(self, path, data):
        json_data = json.dumps(data, cls=DjangoJSONEncoder)
        return self.client.put(path, content_type='application/json', data=json_data)

    def test_get_patient_detail(self):
        self.assertStatusCode('/records/patient/%s' % self.patient.id, 200)

    def test_try_to_get_patient_detail_for_nonexistent_patient(self):
        self.assertStatusCode('/records/patient/%s' % 1234, 404)

    def test_search_with_hospital_number(self):
        self.assertStatusCode('/records/patient/?hospital_number=AA1111', 200)

    def test_search_with_name(self):
        self.assertStatusCode('/records/patient/?name=John', 200)

    def test_try_to_search_with_no_search_terms(self):
        self.assertStatusCode('/records/patient/', 400)

    def test_get_episode_list(self):
        self.assertStatusCode('/records/episode/', 200)

    def test_create_episode_for_existing_patient(self):
        # First, remove tags from patient's existing episode so it is not
        # active anymore.
        episode = self.patient.episode_set.get()
        episode.set_tag_names([], self.user)

        data = {
            'demographics': self.patient.demographics_set.get().to_dict(self.user),
            'location': {
                'date_of_admission': '2013-08-25',
                'category': 'Inpatient',
                'hospital': 'UCH',
                'ward': 'T13',
                'bed': 10
            }
        }

        response = self.post_json('/records/episode/', data)
        self.assertEqual(201, response.status_code)

    def test_try_to_create_episode_for_existing_patient_with_active_episode(self):
        data = {
            'demographics': self.patient.demographics_set.get().to_dict(self.user),
            'location': {
                'date_of_admission': '2013-08-25',
                'category': 'Inpatient',
                'hospital': 'UCH',
                'ward': 'T13',
                'bed': 10
            }
        }

        response = self.post_json('/records/episode/', data)
        self.assertEqual(400, response.status_code)

    def test_create_episode_for_new_patient(self):
        data = {
            'demographics': {
                'hospital_number': 'BB2222',
                'name': 'Johann Schmidt',
                'date_of_birth': '1970-06-01'
            },
            'location': {
                'date_of_admission': '2013-06-25',
                'category': 'Inpatient',
                'hospital': 'UCH',
                'ward': 'T13',
                'bed': 10
            }
        }
        response = self.post_json('/records/episode/', data)
        self.assertEqual(201, response.status_code)

    def test_create_episode_for_patient_without_hospital_number(self):
        data = {
            'demographics': {
                'hospital_number': '',
                'name': 'Johann Schmidt',
                'date_of_birth': '1970-06-01'
            },
            'location': {
                'date_of_admission': '2013-06-25',
                'category': 'Inpatient',
                'hospital': 'UCH',
                'ward': 'T13',
                'bed': 10
            }
        }
        response = self.post_json('/records/episode/', data)
        self.assertEqual(201, response.status_code)

    def test_update_demographics_subrecord(self):
        demographics = self.patient.demographics_set.get()
        data = {
            'consistency_token': '12345678',
            'id': demographics.id,
            'name': 'Johann Schmidt',
            'date_of_birth': '1972-6-21',
            'hospital_number': 'AA1112',
        }
        response = self.put_json('/records/demographics/%s' % demographics.id, data)
        self.assertEqual(200, response.status_code)

    def test_try_to_update_nonexistent_demographics_subrecord(self):
        response = self.put_json('/records/demographics/1234', {})
        self.assertEqual(404, response.status_code)

    def test_try_to_update_demographics_subrecord_with_old_consistency_token(self):
        demographics = self.patient.demographics_set.get()
        data = {
            'consistency_token': '87654321',
            'id': demographics.id,
            'name': 'Johann Schmidt',
            'date_of_birth': '1972-6-21',
            'hospital_number': 'AA1112',
        }
        response = self.put_json('/records/demographics/%s' % demographics.id, data)
        self.assertEqual(409, response.status_code)

    def test_delete_demographics_subrecord(self):
        # In real application, client prevents deletion of demographics
        # subrecord.
        demographics = self.patient.demographics_set.get()
        response = self.client.delete('/records/demographics/%s' % demographics.id)
        self.assertEqual(200, response.status_code)

    def test_create_demographics_subrecord(self):
        # In real application, client prevents creation of demographics
        # subrecord.
        data = {
            'patient_id': self.patient.id,
            'name': 'Johann Schmidt',
            'date_of_birth': '1972-6-21',
            'hospital_number': 'AA1112',
        }
        response = self.post_json('/records/demographics/', data)
        self.assertEqual(201, response.status_code)

    def test_patient_list_tepmlate_view(self):
        self.assertStatusCode('/templates/patient_list.html/', 200)

    def test_patient_detail_tepmlate_view(self):
        self.assertStatusCode('/templates/patient_detail.html/', 200)

    def test_search_template_view(self):
        self.assertStatusCode('/templates/search.html/', 200)

    def test_add_patient_template_view(self):
        self.assertStatusCode('/templates/modals/add_patient.html/', 200)

    def test_discharge_patient_template_view(self):
        self.assertStatusCode('/templates/modals/discharge_patient.html/', 200)

    def test_delete_item_confirmation_template_view(self):
        self.assertStatusCode('/templates/modals/delete_item_confirmation.html/', 200)

    def test_location_modal_template_view(self):
        self.assertStatusCode('/templates/modals/location.html/', 200)

    def test_list_schema_view(self):
        self.assertStatusCode('/schema/list/', 200)

    def test_detail_schema_view(self):
        self.assertStatusCode('/schema/detail/', 200)
