"""
unittests for opal.core.search.views
"""
import json
from datetime import date

from django.core.serializers.json import DjangoJSONEncoder
from mock import patch

from opal import models
from opal.core.test import OpalTestCase
from opal.core.search import views


class BaseSearchTestCase(OpalTestCase):

    def create_patient(self, first_name, last_name, hospital_number):
        patient, episode = self.new_patient_and_episode_please()
        demographics = patient.demographics_set.get()
        demographics.first_name = first_name
        demographics.surname = last_name
        demographics.hospital_number = hospital_number
        demographics.save()
        return patient, episode

    def setUp(self):
        self.patient, self.episode = self.create_patient(
            "Sean", "Connery", "007"
        )

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
    maxDiff = None

    def setUp(self):
        super(SimpleSearchViewTestCase, self).setUp()
        self.url = '/search/simple/'
        self.view = views.simple_search_view
        self.expected = {
            u'page_number': 1,
            u'object_list': [{
                u'count': 1,
                u'id': self.patient.id,
                u'first_name': u'Sean',
                u'surname': u'Connery',
                u'end': u'15/10/2015',
                u'patient_id': 1,
                u'hospital_number': u'007',
                u'date_of_birth': None,
                u'start': u'15/10/2015',
                u'categories': [u'Inpatient']
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
        request = self.rf.get("%s?query=Co" % self.url)
        request.user = self.user
        resp = self.view(request)
        data = json.loads(resp.content)
        self.assertEqual(self.expected, data)

    # Searching for a patient that exists by partial HN match
    def test_patient_exists_partial_number(self):
        request = self.rf.get('%s?query=07' % self.url)
        request.user = self.user
        resp = self.view(request)
        data = json.loads(resp.content)
        self.assertEqual(self.expected, data)

    # Searching for a patient that exists by name
    def test_patient_exists_name(self):
        request = self.rf.get('%s?query=Connery' % self.url)
        request.user = self.user
        resp = self.view(request)
        data = json.loads(resp.content)
        self.assertEqual(self.expected, data)

    # Searching for a patient that doesn't exist by Hospital Number
    def test_patient_does_not_exist_number(self):
        request = self.rf.get('%s?query=notareanumber' % self.url)
        request.user = self.user
        resp = self.view(request)
        data = json.loads(resp.content)
        self.assertEqual(self.empty_expected, data)

    # Searching for a patient that doesn't exist by name
    def test_patient_does_not_exist_name(self):
        request = self.rf.get('%s/?query=notareaname' % self.url)
        request.user = self.user
        resp = self.view(request)
        data = json.loads(resp.content)
        self.assertEqual(self.empty_expected, data)

    # Searching for a patient that exists by Hospital Number
    def test_patient_exists_number(self):
        request = self.rf.get('%s/?query=007' % self.url)
        request.user = self.user
        resp = self.view(request)
        data = json.loads(resp.content)
        self.assertEqual(self.expected, data)

    # searching by James Bond should only yield James Bond
    def test_incomplete_matching(self):
        james_patient, sam_episode = self.create_patient(
            "James", "Bond", "23412"
        )
        sam_patient, sam_episode = self.create_patient(
            "Samantha", "Bond", "23432"
        )
        blofeld_patient, blofeld_episode = self.create_patient(
            "Ernst", "Blofeld", "23422"
        )
        request = self.rf.get('{}/?query=James%20Bond'.format(self.url))
        request.user = self.user
        resp = self.view(request)
        data = json.loads(resp.content)["object_list"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["first_name"], "James")
        self.assertEqual(data[0]["surname"], "Bond")


class SearchTemplateTestCase(OpalTestCase):

    def test_search_template_view(self):
        self.assertStatusCode('/search/templates/search.html/', 200)


class ExtractSearchViewTestCase(BaseSearchTestCase):

    def test_post(self):
        data = json.dumps([
            {
                u'page_number': 1,
                u'column': u'demographics',
                u'field': u'Surname',
                u'combine': u'and',
                u'query': u'Connery',
                u'queryType': u'Equals'
            }
        ])
        request = self.rf.post('extract')
        request.user = self.user
        view = views.ExtractSearchView()
        view.request = request
        with patch.object(view.request, 'read') as mock_read:
            mock_read.return_value = data

            resp = json.loads(view.post().content)
            self.assertEqual(1, resp['total_count'])
            self.assertEqual(self.patient.id, resp['object_list'][0]['patient_id'])


class FilterViewTestCase(OpalTestCase):

    def test_get(self):
        filt = models.Filter(user=self.user, name='testfilter', criteria='[]').save()
        self.assertEqual(1, models.Filter.objects.count())

        view = views.FilterView()
        view.request = self.rf.get('/filter')
        view.request.user = self.user

        data = json.loads(view.get().content)
        self.assertEqual([{'name': 'testfilter', 'criteria': [], 'id': 1}], data)

    def test_post(self):
        view = views.FilterView()
        view.request = self.rf.post('/filter')
        view.request.user = self.user
        with patch.object(view.request, 'read') as mock_read:
            mock_read.return_value =  '{"name": "posttestfilter", "criteria": "[]"}'

            self.assertEqual(0, models.Filter.objects.count())
            view.post()
            self.assertEqual(1, models.Filter.objects.count())


class FilterDetailViewTestCase(OpalTestCase):

    def test_get(self):
        filt = models.Filter(user=self.user, name='testfilter', criteria='[]')
        filt.save()
        request = self.rf.get('/filter/1/')
        request.user = self.user
        data = json.loads(views.FilterDetailView.as_view()(request, pk=filt.pk).content)
        self.assertEqual({'name': 'testfilter', 'criteria': [], 'id': filt.id}, data)
