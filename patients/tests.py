import json
from django.test import TestCase
from django.contrib.auth.models import User
from patients import models
from patients.models import Patient, Episode


class PatientTest(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create()

    def test_demographics_subrecord_created(self):
        self.assertEqual(1, self.patient.demographics_set.count())

    def test_can_create_episode(self):
        episode = self.patient.create_episode()
        self.assertEqual(Episode, type(episode))

    def test_cannot_create_episode_if_has_active_episode(self):
        pass

class EpisodeTest(TestCase):
    fixtures = ['patients_users']

    def setUp(self):
        self.patient = Patient.objects.create()
        self.episode = self.patient.create_episode()

    def test_location_subrecord_created(self):
        self.assertEqual(1, self.episode.location_set.count())

    def test_can_set_tags(self):
        user = User.objects.get(pk=1)

        for tag_names in [
            ['microbiology', 'mine'],
            ['microbiology', 'hiv'],
        ]:
            self.episode.set_tags(tag_names, user)
            self.assertEqual(tag_names, self.episode.get_tags(user))

    def test_user_cannot_see_other_users_mine_tag(self):
        user1 = User.objects.get(pk=1)
        user2 = User.objects.get(pk=2)

        self.episode.set_tags(['hiv', 'mine'], user1)
        self.assertEqual(['hiv'], self.episode.get_tags(user2))




    def test_active_if_tagged_by_non_mine_tag(self):
        pass


#class PatientTest(TestCase):
#    fixtures = ['patients_users', 'patients_options', 'patients_patients']
#
#    def setUp(self):
#        self.assertTrue(self.client.login(username='superuser', password='password'))
#        self.patient = models.Patient.objects.get(pk=1)
#        self.demographics = self.patient.demographics_set.all()[0]
#        self.location = self.patient.location_set.all()[0]
#        self.first_diagnosis = self.patient.diagnosis_set.all()[0]
#
#    def load_expected_data(self, filename):
#        return json.load(open('patients/test_data/%s.json' % filename))
#
#    @property
#    def base_url(self):
#        return '/records/'
#
#    def get(self, sub_url):
#        return self.client.get(self.base_url + sub_url)
#
#    def post(self, sub_url, data):
#        data['patient_id'] = self.patient.id
#        json_data = json.dumps(data)
#        return self.client.post(self.base_url + sub_url, content_type='application/json', data=json_data)
#
#    def put(self, sub_url, data):
#        data['patient_id'] = self.patient.id
#        json_data = json.dumps(data)
#        return self.client.put(self.base_url + sub_url, content_type='application/json', data=json_data)
#
#    def assert_status_code(self, expected_status_code, rsp):
#        self.assertEqual(expected_status_code, rsp.status_code)
#
#    def assert_json_content(self, expected_data, rsp, expect_consistency_token=False):
#        content = json.loads(rsp.content)
#        if expect_consistency_token:
#            try:
#                content.pop('consistency_token')
#            except KeyError:
#                raise AssertionError('No consistency token')
#        self.assertEqual(expected_data, content)
#
#    def assert_has_tags(self, expected_tags, patient_id):
#        patient = models.Patient.objects.get(pk=patient_id)
#        self.assertItemsEqual(expected_tags, [t.tag_name for t in patient.tagging_set.all()])
#
#
#    def test_can_access_patient(self):
#        rsp = self.client.get('/records/patient/%s/' % self.patient.id)
#        self.assert_status_code(200, rsp)
#        self.assert_json_content(self.load_expected_data('patient'), rsp)
#
#    def test_can_access_episode(self):
#        rsp = self.client.get('/records/episode/%s/' % self.episode.id)
#        self.assert_status_code(200, rsp)
#        self.assert_json_content(self.load_expected_data('episode'), rsp)
#
#    def test_can_create_episode_for_new_patient(self):
#        pass
#
#    def test_can_create_episode_for_existing_patient(self):
#        pass
#
#    def test_cannot_create_episode_for_existing_patient_with_active_episode(self):
#        pass
#
#
#    def test_can_create_episode(self):
#        data = {
#            'demographics': {
#                'hospital_number': 'BB2222',
#                'name': 'Johann Schmidt',
#                'date_of_birth': '1970-06-01'
#            },
#            'location': {
#                'date_of_admission': '2013-06-25',
#                'category': 'Inpatient',
#                'hospital': 'UCH',
#                'ward': 'T13',
#                'bed': 10
#            }
#        }
#        rsp = self.client.post('/records/episode/', content_type='application/json', data=json.dumps(data))
#        self.assert_status_code(201, rsp)
#
#    def test_can_access_demographics(self):
#        rsp = self.get('demographics/%s/' % self.demographics.id)
#        expected_data = {
#            'patient_id': self.patient.id,
#            'id': self.demographics.id,
#            'name': 'John Smith',
#            'date_of_birth': '1972-06-20',
#            'hospital_number': 'AA1111',
#        }
#        self.assert_status_code(200, rsp)
#        self.assert_json_content(expected_data, rsp, expect_consistency_token=True)
#
#    def test_can_update_demographics(self):
#        name = 'Jan Smits'
#        date_of_birth = '1972-06-21'
#        data = {'name': name, 'date_of_birth': date_of_birth, 'consistency_token': '12345678'}
#        rsp = self.put('demographics/%s/' % self.demographics.id, data)
#        expected_data = {
#            'patient_id': self.patient.id,
#            'id': self.demographics.id,
#            'name': name,
#            'date_of_birth': date_of_birth,
#            'hospital_number': 'AA1111',
#        }
#        self.assert_status_code(200, rsp)
#        self.assert_json_content(expected_data, rsp, expect_consistency_token=True)
#
#    def test_can_access_location(self):
#        rsp = self.get('location/%s/' % self.location.id)
#        expected_data = {
#            'patient_id': self.patient.id,
#            'id': self.location.id,
#            'category': 'Inpatient',
#            'hospital': 'UCH',
#            'ward': 'T10',
#            'bed': '13',
#            'date_of_admission': '2013-07-25',
#            'discharge_date': None,
#            'tags': {'microbiology': True, 'mine': True},
#        }
#        self.assert_status_code(200, rsp)
#        self.assert_json_content(expected_data, rsp, expect_consistency_token=True)
#
#    def test_can_update_location(self):
#        ward = 'T11'
#        date_of_admission = '2013-07-24'
#        data = {
#            'consistency_token': '12345678',
#            'ward': ward,
#            'date_of_admission': date_of_admission,
#            'tags': {'mine': True}
#        }
#        rsp = self.put('location/%s/' % self.location.id, data)
#        expected_data = {
#            'patient_id': self.patient.id,
#            'id': self.location.id,
#            'category': 'Inpatient',
#            'hospital': 'UCH',
#            'ward': ward,
#            'bed': '13',
#            'date_of_admission': date_of_admission,
#            'discharge_date': None,
#            'tags': {'mine': True},
#        }
#        self.assert_status_code(200, rsp)
#        self.assert_json_content(expected_data, rsp, expect_consistency_token=True)
#
#    def test_updating_location_updates_tags_1(self):
#        data = {
#                'consistency_token': '12345678',
#                'tags': {'mine': True, 'hiv': True}
#        }
#        self.put('location/%s/' % self.location.id, data)
#        self.assert_has_tags(['hiv', 'mine'], self.patient.id)
#
#    def test_updating_location_updates_tags_2(self):
#        data = {
#                'consistency_token': '12345678',
#                'tags': {'microbiology': True, 'hiv': False}
#        }
#        self.put('location/%s/' % self.location.id, data)
#        self.assert_has_tags(['microbiology'], self.patient.id)
#
#    def test_updating_location_updates_tags_3(self):
#        data = {
#                'consistency_token': '12345678',
#                'tags': {'mine': True, 'tropical_diseases': False}
#        }
#        self.put('location/%s/' % self.location.id, data)
#        self.assert_has_tags(['mine'], self.patient.id)
#
#    def test_can_access_diagnosis(self):
#        rsp = self.get('diagnosis/%d/' % self.first_diagnosis.id)
#        expected_data = {
#            'patient_id': self.patient.id,
#            'id': self.first_diagnosis.id,
#            'condition': 'Some condition',
#            'provisional': False,
#            'details': '',
#            'date_of_diagnosis': '2013-07-25',
#        }
#        self.assert_status_code(200, rsp)
#        self.assert_json_content(expected_data, rsp, expect_consistency_token=True)
#
#    def test_can_create_diagnosis_with_existing_condition(self):
#        data = {
#            'condition': 'Some condition',
#            'provisional': False,
#            'details': 'Have some details',
#            'date_of_diagnosis': '2013-07-25',
#        }
#        rsp = self.post('diagnosis/', data)
#        diagnosis = self.patient.diagnosis_set.get(pk=json.loads(rsp.content)['id'])
#        expected_data = {
#            'patient_id': self.patient.id,
#            'id': diagnosis.id,
#            'condition': 'Some condition',
#            'provisional': False,
#            'details': 'Have some details',
#            'date_of_diagnosis': '2013-07-25',
#        }
#        self.assert_status_code(201, rsp)
#        self.assert_json_content(expected_data, rsp, expect_consistency_token=True)
#        self.assertIsNotNone(diagnosis.condition_fk)
#        self.assertEqual('', diagnosis.condition_ft)
#
#    def test_can_create_diagnosis_with_new_condition(self):
#        data = {
#            'condition': 'Some other condition',
#            'provisional': False,
#            'details': 'Have some details',
#            'date_of_diagnosis': '2013-07-25',
#        }
#        rsp = self.post('diagnosis/', data)
#        diagnosis = self.patient.diagnosis_set.get(pk=json.loads(rsp.content)['id'])
#        expected_data = {
#            'patient_id': self.patient.id,
#            'id': diagnosis.id,
#            'condition': 'Some other condition',
#            'provisional': False,
#            'details': 'Have some details',
#            'date_of_diagnosis': '2013-07-25',
#        }
#        self.assert_status_code(201, rsp)
#        self.assert_json_content(expected_data, rsp, expect_consistency_token=True)
#        self.assertIsNone(diagnosis.condition_fk)
#        self.assertEqual('Some other condition', diagnosis.condition_ft)
#
#    def test_can_update_diagnosis(self):
#        data = {
#            'consistency_token': '12345678',
#            'condition': 'Some other condition'
#        }
#        rsp = self.put('diagnosis/%d/' % self.first_diagnosis.id, data)
#        expected_data = {
#            'patient_id': self.patient.id,
#            'id': self.first_diagnosis.id,
#            'condition': 'Some other condition',
#            'provisional': False,
#            'details': '',
#            'date_of_diagnosis': '2013-07-25',
#        }
#        diagnosis = self.patient.diagnosis_set.get(pk=self.first_diagnosis.id)
#        self.assert_status_code(200, rsp)
#        self.assert_json_content(expected_data, rsp, expect_consistency_token=True)
#        self.assertIsNone(diagnosis.condition_fk)
#        self.assertEqual('Some other condition', diagnosis.condition_ft)
#
#    def test_updating_with_wrong_consistency_token_gives_409(self):
#        data = {
#            'consistency_token': '87654321',
#            'condition': 'Some other condition'
#        }
#        rsp = self.put('diagnosis/%d/' % self.first_diagnosis.id, data)
#        self.assert_status_code(409, rsp)
#
#    def test_searching_without_search_terms_is_client_error(self):
#        rsp = self.client.get('/records/patient/')
#        self.assert_status_code(400, rsp)
#
#    def test_can_search_by_name(self):
#        rsp = self.client.get('/records/patient/?name=John')
#        self.assert_status_code(200, rsp)
#        self.assert_json_content([self.load_expected_data('patient')], rsp)
#
#    def test_can_search_by_hospital_number(self):
#        rsp = self.client.get('/records/patient/?hospital_number=AA1111')
#        self.assert_status_code(200, rsp)
#        self.assert_json_content([self.load_expected_data('patient')], rsp)
#
#    def test_can_access_list_schema(self):
#        rsp = self.client.get('/schema/list/')
#        self.assert_status_code(200, rsp)
#
#    def test_can_access_detail_schema(self):
#        rsp = self.client.get('/schema/detail/')
#        self.assert_status_code(200, rsp)
#
#    def test_can_access_patient_list_template(self):
#        rsp = self.client.get('/templates/patient_list.html/')
#        self.assert_status_code(200, rsp)
#
#    def test_can_access_patient_detail_template(self):
#        rsp = self.client.get('/templates/patient_detail.html/')
#        self.assert_status_code(200, rsp)
#
#    def test_can_access_search_template(self):
#        rsp = self.client.get('/templates/search.html/')
#        self.assert_status_code(200, rsp)
#
#    def test_field_schema_correct_for_demographics(self):
#        schema = models.Demographics.build_field_schema()
#        expected_schema = [
#                {'name': 'consistency_token', 'type': 'token'},
#                {'name': 'name', 'type': 'string'},
#                {'name': 'hospital_number', 'type': 'string'},
#                {'name': 'date_of_birth', 'type': 'date'},
#        ]
#        self.assertEqual(expected_schema, schema)
#
#    def test_field_schema_correct_for_location(self):
#        schema = models.Location.build_field_schema()
#        expected_schema = [
#                {'name': 'consistency_token', 'type': 'token'},
#                {'name': 'category', 'type': 'string'},
#                {'name': 'hospital', 'type': 'string'},
#                {'name': 'ward', 'type': 'string'},
#                {'name': 'bed', 'type': 'string'},
#                {'name': 'date_of_admission', 'type': 'date'},
#                {'name': 'discharge_date', 'type': 'date'},
#                {'name': 'tags', 'type': 'list'},
#        ]
#        self.assertEqual(expected_schema, schema)
#
