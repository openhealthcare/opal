"""
unittests for opal.core.search.views
"""
import json
from datetime import date
from django.core.serializers.json import DjangoJSONEncoder

from opal import models
from opal.core.test import OpalTestCase
from opal.core.search import views


class BaseSearchTestCase(OpalTestCase):
    def setUp(self):
        self.patient = models.Patient.objects.create()
        self.episode = self.patient.create_episode()
        self.demographics = self.patient.demographics_set.get()
        self.demographics.name = 'Sean Connery'
        self.demographics.hospital_number = '007'
        self.demographics.save()

    def tearDown(self):
        self.patient.delete()
        super(BaseSearchTestCase, self).tearDown()


class PatientSearchTestCase(BaseSearchTestCase):

    def setUp(self):
        self.url = '/search/patient/'
        self.view = views.patient_search_view
        super(PatientSearchTestCase, self).setUp()

    # Searching for a patient that doesn't exist by Hospital Number
    def test_patient_does_not_exist_number(self):
        request = self.rf.get('%s?hospital_number=notareanumber' % self.url)
        request.user = self.user
        resp = self.view(request)
        data = json.loads(resp.content)
        self.assertEqual([], data)

    # Searching for a patient that exists by Hospital Number
    def test_patient_exists_number(self):
        request = self.rf.get('/search/patient/?hospital_number=007')
        request.user = self.user
        resp = self.view(request)
        data = json.loads(resp.content)
        expected = [self.patient.to_dict(self.user)]

        expected = json.loads(json.dumps(expected, cls=DjangoJSONEncoder))
        self.assertEqual(expected, data)

    # TODO:
    # Searching for a patient that exists but only has episodes that are
    # restricted teams that the user is not a member of.

    def test_must_provide_hospital_number(self):
        request = self.rf.get('/search/patient/')
        request.user = self.user
        resp = self.view(request)
        self.assertEqual(400, resp.status_code)


class SimpleSearchViewTestCase(BaseSearchTestCase):

    def setUp(self):
        super(SimpleSearchViewTestCase, self).setUp()
        self.url = '/search/simple/'
        self.view = views.simple_search_view
        self.expected = {
            u'page_number': 1,
            u'object_list': [{
                u'count': 1,
                u'id': self.patient.id,
                u'name': u'Sean Connery',
                u'end_date': '2015-10-15',
                u'episode_id': 1,
                u'hospital_number': u'007',
                u'date_of_birth': None,
                u'start_date': '2015-10-15',
                u'categories': [u'inpatient']
            }],
            u'total_count': 1,
            u'total_pages': 1,
        }

        self.empty_expected = {
            "page_number": 1,
            "object_list": [],
            "total_pages": 1,
            "total_count": 0
        }
        self.episode.date_of_episode = date(
            day=15, month=10, year=2015
        )
        self.episode.save()

    def test_must_provide_name_or_hospital_number(self):
        request = self.rf.get(self.url)
        request.user = self.user
        resp = self.view(request)
        self.assertEqual(400, resp.status_code)

    # Searching for a patient that exists by partial name match
    def test_patient_exists_partial_name(self):
        request = self.rf.get("%s?name=Sean" % self.url)
        request.user = self.user
        resp = self.view(request)
        data = json.loads(resp.content)
        self.assertEqual(self.expected, data)

    # Searching for a patient that exists by partial HN match
    def test_patient_exists_partial_number(self):
        request = self.rf.get('%s?hospital_number=07' % self.url)
        request.user = self.user
        resp = self.view(request)
        data = json.loads(resp.content)
        self.assertEqual(self.expected, data)

    # Searching for a patient that exists by name
    def test_patient_exists_name(self):
        request = self.rf.get('%s?name=Sean Connery' % self.url)
        request.user = self.user
        resp = self.view(request)
        data = json.loads(resp.content)
        self.assertEqual(self.expected, data)

    # Searching for a patient that doesn't exist by Hospital Number
    def test_patient_does_not_exist_number(self):
        request = self.rf.get('%s?hospital_number=notareanumber' % self.url)
        request.user = self.user
        resp = self.view(request)
        data = json.loads(resp.content)
        self.assertEqual(self.empty_expected, data)

    # Searching for a patient that doesn't exist by name
    def test_patient_does_not_exist_name(self):
        request = self.rf.get('%s/?name=notareaname' % self.url)
        request.user = self.user
        resp = self.view(request)
        data = json.loads(resp.content)
        self.assertEqual(self.empty_expected, data)

    # Searching for a patient that exists by Hospital Number
    def test_patient_exists_number(self):
        request = self.rf.get('%s/?hospital_number=007' % self.url)
        request.user = self.user
        resp = self.view(request)
        data = json.loads(resp.content)
        self.assertEqual(self.expected, data)


class SearchTemplateTestCase(OpalTestCase):

    def test_search_template_view(self):
        self.assertStatusCode('/search/templates/search.html/', 200)
