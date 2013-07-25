import json
from django.test import TestCase
from django.contrib.auth.models import User
from options.models import option_models
from patients.models import Patient

class PatientTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'testuser@exmample.com', 'password')
        self.client.login(username='testuser', password='password')
        self.patient = Patient.objects.create()

    @property
    def base_url(self):
        return '/patient/%d/' % self.patient.id

    def get(self, sub_url):
        return self.client.get(self.base_url + sub_url)

    def post(self, sub_url, data):
        data['patient'] = self.patient.id
        json_data = json.dumps(data)
        return self.client.post(self.base_url + sub_url, content_type='application/json', data=json_data)

    def put(self, sub_url, data):
        data['patient'] = self.patient.id
        json_data = json.dumps(data)
        return self.client.put(self.base_url + sub_url, content_type='application/json', data=json_data)

    def test_can_access_patient_list(self):
        rsp = self.client.get('/patient/')
        self.assertEqual(200, rsp.status_code)

    def test_can_access_patient(self):
        rsp = self.client.get('/patient/%s/' % self.patient.id)
        self.assertEqual(200, rsp.status_code)

    def test_can_create_patient(self):
        data = {
            'demographics': {
                'hospital_number': 'AB1234',
                'name': 'Johann Schmidt',
                'date_of_birth': '01/06/1970'
            },
            'location': {
                'date_of_admission': '25/06/2013',
                'category': 'Inpatient',
                'hospital': 'UCH',
                'ward': 'T13',
                'bed': 10
            }
        }
        rsp = self.client.post('/patient/', content_type='application/json', data=json.dumps(data))
        self.assertEqual(201, rsp.status_code)

    def test_can_access_demographics(self):
        rsp = self.get('demographics/%s/' % self.patient.demographics.all()[0].id)
        self.assertEqual(200, rsp.status_code)

    def test_can_update_demographics(self):
        data = {'name': 'John Smith', 'date_of_birth': '01/06/1980'}
        rsp = self.put('demographics/%s/' % self.patient.demographics.all()[0].id, data)
        self.assertEqual(200, rsp.status_code)

    def test_can_access_location(self):
        rsp = self.get('location/%s/' % self.patient.location.all()[0].id)
        self.assertEqual(200, rsp.status_code)

    def test_can_update_location(self):
        data = {
                'hospital': 'UCH',
                'date_of_admission': '01/06/2013',
                'tags': {'mine': True}
        }
        rsp = self.put('location/%s/' % self.patient.location.all()[0].id, data)
        self.assertEqual(200, rsp.status_code)

    def test_can_access_diagnosis(self):
        data = {
            'condition': 'New Condition',
            'provisional': False,
            'details': 'Have some details'
        }
        rsp = self.post('diagnosis/', data)
        rsp = self.get('diagnosis/%d/' % rsp.data['id'])
        self.assertEqual(200, rsp.status_code)

    def test_can_create_diagnosis_with_existing_condition(self):
        option_models['condition'].objects.create(name='Existing Condition')
        data = {
            'condition': 'Existing Condition',
            'provisional': False,
            'details': 'Have some details'
        }
        rsp = self.post('diagnosis/', data)
        self.assertEqual(201, rsp.status_code)
        diagnosis = self.patient.diagnosis.get(pk=rsp.data['id'])
        self.assertIsNotNone(diagnosis.condition_fk)
        self.assertEqual('', diagnosis.condition_ft)

    def test_can_create_diagnosis_with_new_condition(self):
        data = {
            'condition': 'New Condition',
            'provisional': False,
            'details': 'Have some details'
        }
        rsp = self.post('diagnosis/', data)
        self.assertEqual(201, rsp.status_code)
        diagnosis = self.patient.diagnosis.get(pk=rsp.data['id'])
        self.assertIsNone(diagnosis.condition_fk)
        self.assertEqual('New Condition', diagnosis.condition_ft)

    def test_can_update_diagnosis(self):
        option_models['condition'].objects.create(name='Existing Condition')
        data = {
            'condition': 'Existing Condition',
            'provisional': False,
            'details': 'Have some details'
        }
        rsp = self.post('diagnosis/', data)
        data = {
            'condition': 'New Condition'
        }
        rsp = self.put('diagnosis/%d/' % rsp.data['id'], data)
        self.assertEqual(200, rsp.status_code)
        diagnosis = self.patient.diagnosis.get(pk=rsp.data['id'])
        self.assertIsNone(diagnosis.condition_fk)
        self.assertEqual('New Condition', diagnosis.condition_ft)
