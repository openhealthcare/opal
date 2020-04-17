"""
unittests for opal.core.search.views
"""
import json
from datetime import date

from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from unittest.mock import patch, mock_open

from opal import models
from opal.tests import models as tmodels
from opal.core.test import OpalTestCase
from opal.core.search import views


class BaseSearchTestCase(OpalTestCase):

    def create_patient(self, first_name, last_name, hospital_number):
        patient, episode = self.new_patient_and_episode_please()
        demographics = patient.demographics()
        demographics.first_name = first_name
        demographics.surname = last_name
        demographics.hospital_number = hospital_number
        demographics.save()
        return patient, episode

    def setUp(self):
        self.patient, self.episode = self.create_patient(
            "Sean", "Connery", "007"
        )

    def get_logged_in_request(self, url=None):
        if url is None:
            url = "/"
        request = self.rf.get(url)
        request.user = self.user
        return request

    def get_not_logged_in_request(self, url=None):
        if url is None:
            url = "/"
        request = self.rf.get(url)
        request.user = AnonymousUser()
        return request

    def get_response(self, url=None, view=None):
        request = self.get_logged_in_request(url)
        if view is None:
            view = self.view
        return self.view(request)

    def tearDown(self):
        self.patient.delete()
        super(BaseSearchTestCase, self).tearDown()


class PatientSearchTestCase(BaseSearchTestCase):

    def setUp(self):
        self.url = '/search/patient/'
        self.view = views.patient_search_view
        super(PatientSearchTestCase, self).setUp()

    def test_not_logged_in(self):
        request = self.get_not_logged_in_request()
        with self.assertRaises(PermissionDenied):
            self.view(request)

    # Searching for a patient that doesn't exist by Hospital Number
    def test_patient_does_not_exist_number(self):
        url = '%s?hospital_number=notareanumber' % self.url
        resp = self.get_response(url)
        data = json.loads(resp.content.decode('UTF-8'))
        self.assertEqual([], data)

    # Searching for a patient that exists by Hospital Number
    def test_patient_exists_number(self):
        url = '/search/patient/?hospital_number=007'
        resp = self.get_response(url)
        data = json.loads(resp.content.decode('UTF-8'))
        expected = [self.patient.to_dict(self.user)]

        expected = json.loads(json.dumps(expected, cls=DjangoJSONEncoder))
        self.assertEqual(expected, data)

    def test_patient_number_with_hash(self):
        demographics = self.patient.demographics()
        demographics.hospital_number = "#007"
        demographics.save()
        url = '/search/patient/?hospital_number=%23007'
        resp = self.get_response(url)
        data = json.loads(resp.content.decode('UTF-8'))
        expected = [self.patient.to_dict(self.user)]
        expected = json.loads(json.dumps(expected, cls=DjangoJSONEncoder))
        self.assertEqual(expected, data)

    def test_patient_number_with_slash(self):
        demographics = self.patient.demographics()
        demographics.hospital_number = "/007"
        demographics.save()
        url = '/search/patient/?hospital_number=%2F007'
        resp = self.get_response(url)
        data = json.loads(resp.content.decode('UTF-8'))
        expected = [self.patient.to_dict(self.user)]
        expected = json.loads(json.dumps(expected, cls=DjangoJSONEncoder))
        self.assertEqual(expected, data)

    def test_patient_number_with_question_mark(self):
        demographics = self.patient.demographics()
        demographics.hospital_number = "?007"
        demographics.save()
        url = '/search/patient/?hospital_number=%3F007'
        resp = self.get_response(url)
        data = json.loads(resp.content.decode('UTF-8'))
        expected = [self.patient.to_dict(self.user)]
        expected = json.loads(json.dumps(expected, cls=DjangoJSONEncoder))
        self.assertEqual(expected, data)

    def test_patient_number_with_ampersand(self):
        demographics = self.patient.demographics()
        demographics.hospital_number = "&007"
        demographics.save()
        url = '/search/patient/?hospital_number=%26007'
        resp = self.get_response(url)
        data = json.loads(resp.content.decode('UTF-8'))
        expected = [self.patient.to_dict(self.user)]
        expected = json.loads(json.dumps(expected, cls=DjangoJSONEncoder))
        self.assertEqual(expected, data)


    # TODO:
    # Searching for a patient that exists but only has episodes that are
    # restricted teams that the user is not a member of.

    def test_must_provide_hospital_number(self):
        url = "/search/patient/"
        resp = self.get_response(url)
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
                u'first_name': u'Sean',
                u'surname': u'Connery',
                u'end': u'15/10/2015',
                u'patient_id': self.patient.id,
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
        dt = date(
            day=15, month=10, year=2015
        )
        self.episode.date_of_episode = dt
        self.episode.start = dt
        self.episode.end = dt
        self.episode.save()

    def test_not_logged_in(self):
        request = self.get_not_logged_in_request()
        with self.assertRaises(PermissionDenied):
            self.view(request)

    def test_must_provide_name_or_hospital_number(self):
        resp = self.get_response(self.url)
        self.assertEqual(400, resp.status_code)

    # Searching for a patient that exists by partial name match
    def test_patient_exists_partial_name(self):
        resp = self.get_response("%s?query=Co" % self.url)
        data = json.loads(resp.content.decode('UTF-8'))
        self.assertEqual(self.expected, data)

    # Searching for a patient that exists by partial HN match
    def test_patient_exists_partial_number(self):
        resp = self.get_response('%s?query=07' % self.url)
        data = json.loads(resp.content.decode('UTF-8'))
        self.assertEqual(self.expected, data)

    # Searching for a patient that exists by name
    def test_patient_exists_name(self):
        resp = self.get_response('%s?query=Connery' % self.url)
        data = json.loads(resp.content.decode('UTF-8'))
        self.assertEqual(self.expected, data)

    # Searching for a patient that doesn't exist by Hospital Number
    def test_patient_does_not_exist_number(self):
        resp = self.get_response('%s?query=notareanumber' % self.url)
        data = json.loads(resp.content.decode('UTF-8'))
        self.assertEqual(self.empty_expected, data)

    # Searching for a patient that doesn't exist by name
    def test_patient_does_not_exist_name(self):
        request = self.rf.get('%s/?query=notareaname' % self.url)
        request.user = self.user
        resp = self.view(request)
        data = json.loads(resp.content.decode('UTF-8'))
        self.assertEqual(self.empty_expected, data)

    # Searching for a patient that exists by Hospital Number
    def test_patient_exists_number(self):
        request = self.rf.get('%s/?query=007' % self.url)
        request.user = self.user
        resp = self.view(request)
        data = json.loads(resp.content.decode('UTF-8'))
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
        resp = self.get_response('{}/?query=James%20Bond'.format(self.url))
        data = json.loads(resp.content.decode('UTF-8'))["object_list"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["first_name"], "James")
        self.assertEqual(data[0]["surname"], "Bond")

    def test_number_of_queries(self):
        """ Pagination should make sure we
            do the same number of queries
            despite the number of results.
        """
        # we need to make sure we're all logged in before we start
        self.assertIsNotNone(self.user)
        for i in range(100):
            self.create_patient(
                "James", "Bond", str(i)
            )

        with self.assertNumQueries(26):
            self.get_response('{}/?query=Bond'.format(self.url))

        for i in range(20):
            self.create_patient(
                "James", "Blofelt", str(i)
            )

        with self.assertNumQueries(26):
            self.get_response('{}/?query=Blofelt'.format(self.url))

    def test_with_multiple_patient_episodes(self):
        self.patient.create_episode()
        blofeld_patient, blofeld_episode = self.create_patient(
            "Ernst", "Blofeld", "23422"
        )
        response = json.loads(
            self.get_response(
                '{}/?query=Blofeld'.format(self.url)
            ).content.decode('UTF-8')
        )
        expected = {
            "total_pages": 1,
            "object_list": [{
                "count": 1,
                "first_name": "Ernst",
                "surname": "Blofeld",
                "start": None,
                "patient_id": blofeld_patient.id,
                "hospital_number": "23422",
                "date_of_birth": None,
                "end": None,
                "categories": ["Inpatient"]
            }],
            "page_number": 1,
            "total_count": 1
        }
        self.assertEqual(response, expected)

    @patch('opal.core.search.views.PAGINATION_AMOUNT', 2)
    def test_patients_more_than_pagination_amount(self):
        """
        Prior to 0.16.0 the implementation would sometimes
        return results with fewer than the number of results
        that should have been on that page.

        This is because a subquery was paginating by the
        number of episodes rather than the number of
        patients.
        """
        blofeld_patient, blofeld_episode = self.create_patient(
            "Ernst", "Blofeld", "23422"
        )
        blofeld_patient.create_episode()

        response = json.loads(
            self.get_response(
                '{}/?query=o'.format(self.url)
            ).content.decode('UTF-8')
        )
        self.assertEqual(len(response["object_list"]), 2)


class SearchTemplateTestCase(OpalTestCase):

    def test_search_template_view(self):
        self.assertStatusCode('/search/templates/search.html/', 200)


class ExtractSearchViewTestCase(BaseSearchTestCase):

    def test_not_logged_in_post(self):
        view = views.ExtractSearchView()
        view.request = self.get_not_logged_in_request()
        with self.assertRaises(PermissionDenied):
            view.post()

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

            resp = json.loads(view.post().content.decode('UTF-8'))
            self.assertEqual(1, resp['total_count'])
            self.assertEqual(self.patient.id, resp['object_list'][0]['patient_id'])

    def test_post_with_no_data(self):
        data = json.dumps([])
        request = self.rf.post('extract')
        request.user = self.user
        view = views.ExtractSearchView()
        view.request = request
        with patch.object(view.request, 'read') as mock_read:
            mock_read.return_value = data
            resp = view.post()
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(json.loads(resp.content.decode('UTF-8')), dict(
                error="No search criteria provied"
            ))


class FilterViewTestCase(BaseSearchTestCase):

    def test_not_logged_in_dispatch(self):
        view = views.FilterView()
        view.request = self.get_not_logged_in_request()

        with self.assertRaises(PermissionDenied):
            view.dispatch()

    def test_logged_in_dispatch(self):
        # we should error if we're logged in
        view = views.FilterView()
        request = self.get_logged_in_request()
        view.request = self.get_logged_in_request()
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)

    def test_get(self):
        filter = models.Filter.objects.create(
            user=self.user, name='testfilter', criteria='[]'
        )
        self.assertEqual(1, models.Filter.objects.count())

        view = views.FilterView()
        view.request = self.rf.get('/filter')
        view.request.user = self.user

        data = json.loads(view.get().content.decode('UTF-8'))
        self.assertEqual(
            [{'name': filter.name, 'criteria': [], 'id': filter.id}], data
        )

    def test_post(self):
        view = views.FilterView()
        view.request = self.rf.post('/filter')
        view.request.user = self.user
        with patch.object(view.request, 'read') as mock_read:
            mock_read.return_value =  '{"name": "posttestfilter", "criteria": "[]"}'

            self.assertEqual(0, models.Filter.objects.count())
            view.post()
            self.assertEqual(1, models.Filter.objects.count())


class FilterDetailViewTestCase(BaseSearchTestCase):

    def setUp(self):
        super(FilterDetailViewTestCase, self).setUp()
        self.filt = models.Filter(user=self.user, name='testfilter', criteria='[]')
        self.filt.save()

    def test_get(self):
        request = self.get_logged_in_request('/filter/1/')
        data = json.loads(views.FilterDetailView.as_view()(
            request, pk=self.filt.pk).content.decode('UTF-8'))
        self.assertEqual({'name': 'testfilter',
                          'criteria': [],
                          'id': self.filt.id}, data)

    def test_filter_detail_no_filter(self):
        view = views.FilterDetailView()
        view.request = self.get_logged_in_request()
        response = view.dispatch(pk=323)
        self.assertEqual(404, response.status_code)

    def test_not_logged_in_dispatch(self):
        view = views.FilterDetailView()
        view.request = self.get_not_logged_in_request()

        with self.assertRaises(PermissionDenied):
            view.dispatch()

    def test_put(self):
        view = views.FilterDetailView()
        view.request = self.get_logged_in_request()
        with patch.object(view.request, "read") as criteria:
            criteria.return_value = json.dumps(
                {'criteria': [], 'name': 'My Name'}
            )
            view.filter = self.filt
            resp = view.put()
            self.assertEqual(200, resp.status_code)

    def test_delete(self):
        view = views.FilterDetailView()
        view.request = self.get_logged_in_request()
        view.filter = self.filt
        view.delete()
        self.assertEqual(0, models.Filter.objects.count())


class ExtractResultViewTestCase(BaseSearchTestCase):

    @patch('celery.result.AsyncResult')
    def test_get(self, async_result):
        view = views.ExtractResultView()
        view.request = self.get_logged_in_request()
        async_result.return_value.state = 'The State'
        resp = view.get(task_id=490)
        self.assertEqual(200, resp.status_code)


class ExtractFileView(BaseSearchTestCase):

    def test_get_not_logged_in(self):
        view = views.ExtractFileView()
        view.request = self.get_not_logged_in_request()
        with self.assertRaises(PermissionDenied):
            resp = view.get(task_id=8902321890)

    @patch('celery.result.AsyncResult')
    def test_get(self, async_result):
        view = views.ExtractFileView()
        view.request = self.get_logged_in_request()
        async_result.return_value.state = 'SUCCESS'
        async_result.return_value.get.return_value = 'foo.txt'

        m = mock_open(read_data='This is a file')
        with patch('opal.core.search.views.open', m, create=True) as m:
            resp = view.get(task_id=437878)
            self.assertEqual(200, resp.status_code)

    @patch('celery.result.AsyncResult')
    def test_get_not_successful(self, async_result):
        view = views.ExtractFileView()
        view.request = self.get_logged_in_request("/")
        async_result.return_value.state = 'FAILURE'
        with self.assertRaises(ValueError):
            view.get(task_id=8902321890)
