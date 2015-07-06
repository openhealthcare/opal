"""
unittests for opal.core.search.views
"""
import json

from django.contrib.auth.models import User
from mock import patch

from opal import models
from opal.core.test import OpalTestCase
from opal.core.search import views

class PatientSearchTestCase(OpalTestCase):

    def setUp(self):
        self.patient = models.Patient.objects.create()
        self.demographics = self.patient.demographics_set.get()
        self.demographics.name = 'Sean Connery'
        self.demographics.hospital_number = '007'
        self.demographics.save()
        self.patient.create_episode()
        OpalTestCase.tearDown(self)
        
    def tearDown(self):
        self.patient.delete()
        OpalTestCase.tearDown(self)

    # Searching for a patient that doesn't exist by Hospital Number
    def test_patient_does_not_exist_number(self):
        request = self.rf.get('/search/patient/?hospital_number=notareanumber')
        request.user = self.user
        resp = views.patient_search_view(request)
        data = json.loads(resp.content)
        self.assertEqual([], data)
        
    # Searching for a patient that doesn't exist by name
    def test_patient_does_not_exist_name(self):
        request = self.rf.get('/search/patient/?name=notareaname')
        request.user = self.user
        resp = views.patient_search_view(request)
        data = json.loads(resp.content)
        self.assertEqual([], data)

    # Searching for a patient that exists by name
    def test_patient_exists_name(self):
        request = self.rf.get('/search/patient/?name=Sean Connery')
        request.user = self.user
        resp = views.patient_search_view(request)
        data = json.loads(resp.content)
        expected = [self.patient.to_dict(self.user)]
        expected = json.loads(json.dumps(expected))
        self.assertEqual(expected, data)

    # Searching for a patient that exists by Hospital Number
    def test_patient_exists_number(self):
        request = self.rf.get('/search/patient/?hospital_number=007')
        request.user = self.user
        resp = views.patient_search_view(request)
        data = json.loads(resp.content)
        expected = [self.patient.to_dict(self.user)]
        expected = json.loads(json.dumps(expected))
        self.assertEqual(expected, data)

    # Searching for a patient that exists by partial HN match
    def test_patient_exists_partial_number(self):
        request = self.rf.get('/search/patient/?hospital_number=07')
        request.user = self.user
        resp = views.patient_search_view(request)
        data = json.loads(resp.content)
        expected = [self.patient.to_dict(self.user)]
        expected = json.loads(json.dumps(expected))
        self.assertEqual(expected, data)

    # Searching for a patient that exists by partial name match
    def test_patient_exists_partial_name(self):
        request = self.rf.get('/search/patient/?name=Sean')
        request.user = self.user
        resp = views.patient_search_view(request)
        data = json.loads(resp.content)
        expected = [self.patient.to_dict(self.user)]
        expected = json.loads(json.dumps(expected))
        self.assertEqual(expected, data)

    # TODO:
    # Searching for a patient that exists but only has episodes that are
    # restricted teams that the user is not a member of.
    
    def test_must_provide_name_or_hospital_number(self):
        request = self.rf.get('/search/patient/')
        request.user = self.user
        resp = views.patient_search_view(request)
        self.assertEqual(400, resp.status_code)
        
        
class SearchTemplateTestCase(OpalTestCase):

    def test_search_template_view(self):
        self.assertStatusCode('/search/templates/search.html/', 200)

