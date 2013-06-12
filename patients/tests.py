import json
from django.test import TestCase
from options.models import option_models
from patients.models import Patient

class PatientTest(TestCase):
    def setUp(self):
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

    def test_can_create_patient(self):
        rsp = self.client.post('/patient/')
        self.assertEqual(201, rsp.status_code)

    def test_can_access_demographics(self):
        rsp = self.get('demographics/')
        self.assertEqual(200, rsp.status_code)

    def test_can_update_demographics(self):
        data = {'name': 'John Smith', 'date_of_birth': '1980-06-01'}
        rsp = self.put('demographics/', data)
        self.assertEqual(200, rsp.status_code)

    def test_can_access_location(self):
        rsp = self.get('location/')
        self.assertEqual(200, rsp.status_code)

    def test_can_update_location(self):
        data = {'hospital': 'UCH', 'date_of_admission': '2013-06-01'}
        rsp = self.put('location/', data)
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
        diagnosis = self.patient.diagnosis_set.get(pk=rsp.data['id'])
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
        diagnosis = self.patient.diagnosis_set.get(pk=rsp.data['id'])
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
        diagnosis = self.patient.diagnosis_set.get(pk=rsp.data['id'])
        self.assertIsNone(diagnosis.condition_fk)
        self.assertEqual('New Condition', diagnosis.condition_ft)

    def test_can_create_past_medical_history(self):
        data = {
            'condition': 'New Condition',
            'year': '2010'
        }
        rsp = self.post('past_medical_history/', data)
        self.assertEqual(201, rsp.status_code)

    def test_can_access_past_medical_history(self):
        data = {
            'condition': 'New Condition',
            'year': '2010'
        }
        rsp = self.post('past_medical_history/', data)
        rsp = self.get('past_medical_history/%d/' % rsp.data['id'])
        self.assertEqual(200, rsp.status_code)

    def test_can_create_general_note(self):
        data = {
            'date': '2013-06-12',
            'comment': 'Malkovich Malkovich'
        }
        rsp = self.post('general_note/', data)
        self.assertEqual(201, rsp.status_code)

    def test_can_access_general_note(self):
        data = {
            'date': '2013-06-12',
            'comment': 'Malkovich Malkovich'
        }
        rsp = self.post('general_note/', data)
        rsp = self.get('general_note/%d/' % rsp.data['id'])
        self.assertEqual(200, rsp.status_code)

    def test_can_create_destination(self):
        data = {
            'destination': 'Solomon Islands',
            'dates': 'May 2013',
            'reason_for_travel': 'Holiday',
            'specific_exposures': 'Bitten by water snake'
        }
        rsp = self.post('destination/', data)
        self.assertEqual(201, rsp.status_code)

    def test_can_access_destination(self):
        data = {
            'destination': 'Solomon Islands',
            'dates': 'May 2013',
            'reason_for_travel': 'Holiday',
            'specific_exposures': 'Bitten by water snake'
        }
        rsp = self.post('destination/', data)
        rsp = self.get('destination/%d/' % rsp.data['id'])
        self.assertEqual(200, rsp.status_code)

    def test_can_create_antimicrobial(self):
        data = {
            'drug': 'Flucytosine'
        }
        rsp = self.post('antimicrobial/', data)
        self.assertEqual(201, rsp.status_code)

    def test_can_access_antimicrobial(self):
        data = {
            'drug': 'Flucytosine'
        }
        rsp = self.post('antimicrobial/', data)
        rsp = self.get('antimicrobial/%d/' % rsp.data['id'])
        self.assertEqual(200, rsp.status_code)

    def test_can_create_microbiology_input(self):
        data = {
            'date': '2013-06-12',
            'initials': 'GP'
        }
        rsp = self.post('microbiology_input/', data)
        self.assertEqual(201, rsp.status_code)

    def test_can_access_microbiology_input(self):
        data = {
            'date': '2013-06-12',
            'initials': 'GP'
        }
        rsp = self.post('microbiology_input/', data)
        rsp = self.get('microbiology_input/%d/' % rsp.data['id'])
        self.assertEqual(200, rsp.status_code)

    def test_can_access_plan(self):
        rsp = self.get('plan/')
        self.assertEqual(200, rsp.status_code)

    def test_can_update_plan(self):
        data = {'plan': 'Chase cultures'}
        rsp = self.put('plan/', data)
        self.assertEqual(200, rsp.status_code)

    def test_can_access_discharge(self):
        rsp = self.get('discharge/')
        self.assertEqual(200, rsp.status_code)

    def test_can_update_discharge(self):
        data = {'discharge': 'Go home'}
        rsp = self.put('discharge/', data)
        self.assertEqual(200, rsp.status_code)

