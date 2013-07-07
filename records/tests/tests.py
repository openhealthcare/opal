import datetime
import json
from django.test import TestCase
from django.test.client import RequestFactory
from django.core import urlresolvers
from records import exceptions, models, urls, views
from records.tests import models as test_models

class BaseTestCase(TestCase):
    def setUp(self):
        self.patient = models.Patient.objects.create()
        self.admission = models.Admission.objects.create(patient=self.patient)
        self.location = test_models.Location.objects.create(
            admission=self.admission,
            ward='T12',
            bed='35',
        )
        self.demographics = test_models.Demographics.objects.create(
            patient=self.patient,
            name='John Smith',
            date_of_birth='1970-1-1'
        )


class ModelTest(BaseTestCase):
    def test_lookup_subrecord_model_by_name(self):
        self.assertEqual(test_models.Demographics, models.get_subrecord_model('demographics'))

    def test_lookup_nonexistent_subrecord_model_by_name(self):
        self.assertIsNone(models.get_subrecord_model('made_up'))

    def test_patient_subrecord_subclass_has_patient(self):
        self.assertEqual(self.patient, self.demographics.patient)

    def test_admission_subrecord_subclass_has_admission(self):
        self.assertEqual(self.admission, self.location.admission)

    def test_admission_subrecord_subclass_has_patient(self):
        self.assertEqual(self.patient, self.location.patient)


class UrlTest(BaseTestCase):
    def assertURLResolves(self, url, func):
        self.assertEqual(func, urlresolvers.resolve(url, 'records.urls').func)

    def test_url_for_patient_create(self):
        self.assertURLResolves('/patient/', views.patient_create)

    def test_url_for_patient_detail(self):
        self.assertURLResolves('/patient/123/', views.patient_detail)

    def test_url_for_admission_create(self):
        self.assertURLResolves('/admission/', views.admission_create)

    def test_url_for_admission_detail(self):
        self.assertURLResolves('/admission/123/', views.admission_detail)

    def test_url_for_subrecord_create(self):
        self.assertURLResolves('/demographics/', views.subrecord_create)

    def test_url_for_subrecord_detail(self):
        self.assertURLResolves('/demographics/123/', views.subrecord_detail)

class SubrecordCreateViewTest(BaseTestCase):
    urls = 'records.urls'

    def test_posting_subrecord_gives_201(self):
        data = {
            'patient_id': self.patient.id,
            'name': 'Jan Smit',
            'date_of_birth': '1980-1-1'
        }
        response = self.client.post('/demographics/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_posting_subrecord_returns_parsable_json(self):
        data = {
            'patient_id': self.patient.id,
            'name': 'Jan Smit',
            'date_of_birth': '1980-1-1'
        }
        response = self.client.post('/demographics/', data=json.dumps(data), content_type='application/json')
        json.loads(response.content)
        # There's no assertion here, but nothing should be raised

    def test_posting_subrecord_with_no_parent_gives_400(self):
        data = {
            'name': 'Jan Smit',
            'date_of_birth': '1980-1-1'
        }
        response = self.client.post('/demographics/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_posting_subrecord_with_invalid_date_gives_400(self):
        data = {
            'patient_id': self.patient.id,
            'name': 'Jan Smit',
            'date_of_birth': 'Blackberry'
        }
        response = self.client.post('/demographics/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

class SubrecordDetailViewTest(BaseTestCase):
    urls = 'records.urls'

    def assertResponseHasStatusCode(self, url, status_code):
        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)

    def test_getting_nonexistent_subrecord_type_gives_404(self):
        self.assertResponseHasStatusCode('/made_up/123/', 404)

    def test_getting_nonexistent_subrecord_gives_404(self):
        self.assertResponseHasStatusCode('/demographics/123/', 404)

    def test_getting_subrecord_gives_200(self):
        self.assertResponseHasStatusCode(
            '/demographics/%d/' % self.demographics.id,
            200
        )

    def test_getting_subrecord_has_json_content_type(self):
        response = self.client.get('/demographics/%d/' % self.demographics.id)
        self.assertEqual('application/json', response['Content-Type'])

    def test_getting_subrecord_returns_parsable_json(self):
        response = self.client.get('/demographics/%d/' % self.demographics.id)
        json.loads(response.content)
        # There's no assertion here, but nothing should be raised

    def test_putting_subrecord_gives_200(self):
        url = '/demographics/%d/' % self.demographics.id
        data = {'consistency_token': self.demographics.consistency_token, 'name': 'Johannes Schmidt'}
        response = self.client.put(url, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)

    def test_putting_invalid_subrecord_gives_400(self):
        url = '/demographics/%d/' % self.demographics.id
        data = {'consistency_token': self.demographics.consistency_token, 'date_of_birth': 'Johannes Schmidt'}
        response = self.client.put(url, data=json.dumps(data))
        self.assertEqual(response.status_code, 400)

    def test_putting_conflicting_subrecord_gives_409(self):
        url = '/demographics/%d/' % self.demographics.id
        data = {'consistency_token': '1234abcd', 'date_of_birth': 'Johannes Schmidt'}
        response = self.client.put(url, data=json.dumps(data))
        self.assertEqual(response.status_code, 409)

class PatientCreateViewTest(BaseTestCase):
    urls = 'records.urls'

    def test_posting_patient_gives_201(self):
        data = {}
        response = self.client.post('/patient/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

class PatientDetailViewTest(BaseTestCase):
    urls = 'records.urls'

    def test_getting_patient_gives_200(self):
        url = '/patient/%d/' % self.patient.id
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

class AdmissionCreateViewTest(BaseTestCase):
    urls = 'records.urls'

    def test_posting_admission_gives_201(self):
        data = {
            'patient_id': self.patient.id,
        }
        response = self.client.post('/admission/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

class AdmissionDetailViewTest(BaseTestCase):
    urls = 'records.urls'

    def test_getting_admission_gives_200(self):
        url = '/admission/%d/' % self.admission.id
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

class SerializationTest(BaseTestCase):
    def assertSerializes(self, serialization, instance):
        reloaded_instance = type(instance).objects.get(pk=instance.id)
        self.assertEqual(serialization, reloaded_instance.serialize())

    def test_patient_subrecord_serializes_correctly(self):
        self.assertSerializes(
            {
                'id': self.demographics.id,
                'patient_id': self.patient.id,
                'name': 'John Smith',
                'date_of_birth': datetime.date(1970, 1, 1),
                'consistency_token': self.demographics.consistency_token,
            },
            self.demographics
        )

    def test_admission_subrecord_serializes_correctly(self):
        self.assertSerializes(
            {
                'id': self.location.id,
                'admission_id': self.admission.id,
                'ward': 'T12',
                'bed': '35',
                'consistency_token': self.location.consistency_token,
            },
            self.location
        )

    def test_admission_serializes_correctly(self):
        self.assertSerializes(
            {
                'id': self.admission.id,
                'location': [{
                    'id': self.location.id,
                    'admission_id': self.admission.id,
                    'ward': 'T12',
                    'bed': '35',
                    'consistency_token': self.location.consistency_token,
                }],
            },
            self.admission
        )

    def test_patient_serializes_correctly(self):
        self.assertSerializes(
            {
                'id': self.patient.id,
                'admissions': [
                    {
                        'id': self.admission.id,
                        'location': [{
                            'id': self.location.id,
                            'admission_id': self.admission.id,
                            'ward': 'T12',
                            'bed': '35',
                            'consistency_token': self.location.consistency_token,
                        }],
                    },
                ],
                'demographics': [{
                    'id': self.demographics.id,
                    'patient_id': self.patient.id,
                    'name': 'John Smith',
                    'date_of_birth': datetime.date(1970, 1, 1),
                    'consistency_token': self.demographics.consistency_token,
                }],
            },
            self.patient
        )


class DeserializationTest(BaseTestCase):
    def update_demographics(self, data):
        data['consistency_token'] = self.demographics.consistency_token
        self.demographics.update(data)

    def test_can_update_patient_subrecord(self):
        name = 'Johannes Schmidt'
        self.update_demographics({'name': name})
        reloaded_demographics = test_models.Demographics.objects.get(pk=self.demographics.id)
        self.assertEqual(reloaded_demographics.name, name)

    def test_update_raises_api_error_if_field_is_unexpected(self):
        with self.assertRaises(exceptions.APIError):
            self.update_demographics({'watermelon': 'pineapple'})

    def test_update_raises_api_error_if_field_value_is_invalid(self):
        with self.assertRaises(exceptions.APIError):
            self.update_demographics({'date_of_birth': 'grapefruit'})

    def test_update_raises_api_error_if_consistency_token_is_absent(self):
        with self.assertRaises(exceptions.APIError):
            self.demographics.update({'name': 'Johannes Schmidt'})

    def test_update_raises_consistency_error_if_consistency_token_incorrect(self):
        with self.assertRaises(exceptions.ConsistencyError):
            self.demographics.update({'consistency_token': '1234abcd', 'name': 'Johannes Schmidt'})

