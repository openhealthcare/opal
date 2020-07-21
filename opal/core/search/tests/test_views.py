"""
unittests for opal.core.search.views
"""
import json
from datetime import date

from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.urls import reverse
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


class SimpleSearchResultsListTestCase(BaseSearchTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("simple_search")
        self.view = views.SimpleSearchResultsList.as_view()

    def test_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/accounts/login/?next={}'.format(
            self.url
        ))

    def test_no_querystring(self):
        view = views.SimpleSearchResultsList()
        view.request = self.get_logged_in_request()
        self.assertEqual(
            view.get_queryset(), []
        )

    def test_duplicate_episodes_for_the_same_patient_are_not_counted(self):
        expected_episode = self.patient.create_episode()
        request = self.rf.get("{}?query=Sean".format(self.url))
        request.user = self.user
        view = views.SimpleSearchResultsList()
        view.request = request
        self.assertEqual(
            list(view.get_queryset()), [expected_episode]
        )

    def test_min_max_page_number_one(self):
        self.assertEqual(
            (1, 7,), views.SimpleSearchResultsList().get_min_max_page_number(1, 100)
        )

    def test_min_max_page_number_two(self):
        self.assertEqual(
            (1, 7,), views.SimpleSearchResultsList().get_min_max_page_number(2, 100)
        )

    def test_min_max_page_number_five(self):
        self.assertEqual(
            (2, 8,), views.SimpleSearchResultsList().get_min_max_page_number(5, 100)
        )

    def test_min_max_page_number_near_end(self):
        self.assertEqual(
            (94, 100,), views.SimpleSearchResultsList().get_min_max_page_number(99, 100)
        )

    def test_min_max_small_result_set(self):
        self.assertEqual(
            (1, 3,), views.SimpleSearchResultsList().get_min_max_page_number(2, 3)
        )

    def test_vanilla_get(self):
        url = "{}?query=Sean".format(self.url)
        self.assertTrue(
            self.client.login(
                username=self.user.username, password=self.PASSWORD
            )
        )
        self.client.get(url)

