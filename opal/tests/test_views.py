"""
Unittests for opal.views
"""
from django import http
from django.core.urlresolvers import reverse
from mock import patch, MagicMock

from opal import models, views
from opal.core import detail
from opal.core.episodes import InpatientEpisode
from opal.core.test import OpalTestCase

# this is used just to import the class for EpisodeListApiTestCase
from opal.tests.test_patient_lists import TaggingTestPatientList # flake8: noqa
from opal.tests import models as testmodels

class BaseViewTestCase(OpalTestCase):

    def setUp(self):
        self.patient = models.Patient.objects.create()
        self.episode = self.patient.create_episode()

    def get_request(self, path):
        request = self.rf.get(path)
        request.user = self.user
        return request

    def should_200(self, viewklass, request):
        view = viewklass.as_view()
        resp = view(request)
        self.assertEqual(200, resp.status_code)

    def setup_view(self, view, request, *args, **kw):
        v = view()
        v.request = request
        v.args = args
        v.kwargs = kw
        return v


class PatientListTemplateViewTestCase(BaseViewTestCase):
    # The Eater Herbivore patient list is defined in
    # opal.tests.test_patient_lists

    def test_dispatch_sets_list(self):
        url = reverse("patient_list_template_view", kwargs=dict(slug="eater-herbivore"))
        request = self.get_request(url)
        view = self.setup_view(views.PatientListTemplateView, request, slug="eater-herbivore")
        view.dispatch(request, slug="eater-herbivore")
        self.assertEqual(TaggingTestPatientList, view.patient_list)

    def test_dispatch_no_list(self):
        url = reverse("patient_list_template_view", kwargs=dict(slug="notalist"))
        request = self.get_request(url)
        view = self.setup_view(views.PatientListTemplateView, request, slug="notalist")
        view.dispatch(request, slug="notalist")
        self.assertEqual(None, view.patient_list)

    def test_episode_list_view(self):
        url = reverse("patient_list_template_view", kwargs=dict(slug="eater-herbivore"))
        request = self.get_request(url)
        view = self.setup_view(views.PatientListTemplateView, request, slug="eater-herbivore")
        view.patient_list = TaggingTestPatientList

        self.assertEqual(200, view.get(request, **view.kwargs).status_code)

    def test_get_context_data(self):
        url = reverse("patient_list_template_view", kwargs=dict(slug="eater-herbivore"))
        request = self.get_request(url)
        view = self.setup_view(views.PatientListTemplateView, request, slug="eater-herbivore")
        view.patient_list = TaggingTestPatientList

        context_data = view.get_context_data(slug="eater-herbivore")
        column_names = [i["name"] for i in context_data["columns"]]
        self.assertEqual(column_names, ["demographics"])

    def test_get_column_context_no_list(self):
        view = views.PatientListTemplateView()
        view.patient_list = None
        ctx = view.get_column_context(slug='notarealthing')
        self.assertEqual([], ctx)

    def test_get_template_names(self):
        url = reverse("patient_list_template_view", kwargs=dict(slug="eater-herbivore"))
        request = self.get_request(url)
        view = self.setup_view(views.PatientListTemplateView, request, slug="eater-herbivore")
        view.patient_list = TaggingTestPatientList

        self.assertEqual(['patient_lists/spreadsheet_list.html'], view.get_template_names())

    def test_get_template_names_no_list(self):
        url = reverse("patient_list_template_view", kwargs=dict(slug="eater-herbivore"))
        request = self.get_request(url)
        view = self.setup_view(views.PatientListTemplateView, request, slug="eater-herbivore")
        view.patient_list = None
        self.assertEqual(['patient_lists/spreadsheet_list.html'], view.get_template_names())


class PatientDetailTemplateViewTestCase(BaseViewTestCase):

    def test_get_context_data_models(self):
        request = self.rf.get('/wat')
        request.user = self.user
        view = views.PatientDetailTemplateView()
        view.request = request
        ctx = view.get_context_data()
        self.assertEqual(testmodels.Colour, ctx['models']['Colour'])

    def test_get_context_data_episode_types(self):
        request = self.rf.get('/wat')
        request.user = self.user
        view = views.PatientDetailTemplateView()
        view.request = request
        ctx = view.get_context_data()
        self.assertIn(InpatientEpisode, ctx['episode_types'])

    def test_get_context_data_detail_views(self):
        request = self.rf.get('/wat')
        request.user = self.user
        view = views.PatientDetailTemplateView()
        view.request = request
        ctx = view.get_context_data()
        expected = list(detail.PatientDetailView.for_user(self.user))
        self.assertEqual(expected, list(ctx['detail_views']))

    def test_default_should_200(self):
        request = self.get_request('/patient_detail.html')
        self.should_200(views.PatientDetailTemplateView, request)


class EpisodeDetailTemplateViewTestCase(BaseViewTestCase):

    def test_get_for_existing_episode(self):
        request = self.get_request('/episode_detail.html')
        view = self.setup_view(views.EpisodeDetailTemplateView, request)
        resp = view.get(request, pk=self.episode.pk)
        self.assertEqual(200, resp.status_code)

    def test_get_for_nonexistent_episode(self):
        request = self.get_request('/episode_detail.html')
        view = self.setup_view(
            views.EpisodeDetailTemplateView, request)
        with self.assertRaises(http.Http404):
            resp = view.get(request, pk=self.episode.pk+345)


class TagsTemplateViewTestCase(BaseViewTestCase):

    def test_default_should_200(self):
        request = self.get_request('/tags_template_modal.html')
        self.should_200(views.TagsTemplateView, request)


class AddEpisodeTemplateViewTestCase(BaseViewTestCase):

    def test_default_should_200(self):
        request = self.get_request(
            '/add_episode_template_modal.html')
        self.should_200(views.AddEpisodeTemplateView, request)


class IndexViewTestCase(BaseViewTestCase):

    def test_should_200(self):
        request = self.get_request('/index.html')
        self.should_200(views.IndexView, request)


class CheckPasswordResetViewTestCase(BaseViewTestCase):

    @patch('opal.views.login')
    def test_login_fails(self, login):
        mockresponse = MagicMock(name='Response')
        mockresponse.status_code = 200
        login.return_value = mockresponse

        response = views.check_password_reset(
            self.get_request('/login/')
        )
        self.assertEqual(mockresponse, response)

    @patch('opal.views.login')
    def test_login_profile_exists_force_change(self, login):
        mockresponse = MagicMock(name='Response')
        mockresponse.status_code = 302
        login.return_value = mockresponse

        self.user.profile.force_password_change = True
        self.user.profile.save()

        response = views.check_password_reset(
            self.get_request('/login/')
        )
        self.assertEqual(302, response.status_code)
        self.assertEqual(
            '/accounts/change-password',
            response.get('Location')
        )

    @patch('opal.views.login')
    def test_login_profile_exists_dont_force_change(self, login):
        mockresponse = MagicMock(name='Response')
        mockresponse.status_code = 302
        login.return_value = mockresponse

        self.user.profile.force_password_change = False
        self.user.profile.save()

        response = views.check_password_reset(
            self.get_request('/login/')
        )
        self.assertEqual(mockresponse, response)


class EpisodeDetailViewTestCase(OpalTestCase):

    def test_episode_detail_view(self):
        self.patient = models.Patient.objects.create()
        self.episode = self.patient.create_episode()
        request = self.rf.get('/episode/detail')
        request.user = self.user
        resp = views.episode_detail_view(request, 1)
        self.assertEqual(200, resp.status_code)

    def test_epidode_detail_view_does_not_exist(self):
        request = self.rf.get('/episode/detail')
        request.user = self.user
        resp = views.episode_detail_view(request, 123)
        self.assertEqual(404, resp.status_code)


class EpisodeListAndCreateViewTestCase(OpalTestCase):
    def test_get(self):
        request = self.rf.get('/episode/detail')
        request.user = self.user
        resp = views.episode_list_and_create_view(request)
        self.assertEqual(200, resp.status_code)


class GetColumnContextTestCase(OpalTestCase):

    def test_column_context(self):
        schema = [testmodels.Colour]

        expected = [
            dict(
                name = 'colour',
                title = 'Colour',
                single = False,
                icon = '',
                list_limit = None,
                template_path = 'records/colour.html',
                detail_template_path = 'records/colour.html',
                header_template_path = ''
            )
        ]
        context = views._get_column_context(schema)
        self.assertEqual(expected, context)


class FormTemplateViewTestCase(BaseViewTestCase):

    def test_200(self):
        request = self.get_request('/colour_form.html')
        view = self.setup_view(
            views.FormTemplateView, request)
        resp = view.dispatch(request, model=testmodels.Colour)
        self.assertEqual(200, resp.status_code)

class ModalTemplateViewTestCase(BaseViewTestCase):

    def test_200(self):
        request = self.get_request('/colour_modal.html')
        view = self.setup_view(
            views.ModalTemplateView, request)
        resp = view.dispatch(request, model=testmodels.Colour)
        self.assertEqual(200, resp.status_code)


class RecordTemplateViewTestCase(BaseViewTestCase):

    def test_200(self):
        request = self.get_request('/colour_record.html')
        view = self.setup_view(
            views.RecordTemplateView, request)
        resp = view.dispatch(request, model=testmodels.Colour)
        self.assertEqual([testmodels.Colour.get_display_template()], resp.template_name)
        self.assertEqual(200, resp.status_code)


class BannedViewTestCase(BaseViewTestCase):
    def test_banned_view(self):
        request = self.get_request('/banned_passwords')
        self.should_200(views.BannedView, request)


class RawTemplateViewTestCase(BaseViewTestCase):

    def test_get_existing_template(self):
        request = self.get_request('modal_base.html')
        view = self.setup_view(
            views.RawTemplateView, request)
        resp = view.dispatch(request, template_name='modal_base.html')
        self.assertEqual(200, resp.status_code)

    def test_get_non_existing_template(self):
        request = self.get_request('not_a_real_template.html')
        view = self.setup_view(
            views.RawTemplateView, request)
        resp = view.dispatch(request, template_name='not_a_real_template.html')
        self.assertEqual(404, resp.status_code)
