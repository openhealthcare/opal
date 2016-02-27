"""
Unittests for opal.views
"""
from django import http
from django.core.urlresolvers import reverse
from mock import patch, MagicMock

from opal import models, views
from opal.tests import models as testmodels
from opal.core.test import OpalTestCase

# this is used just to import the class for EpisodeListApiTestCase
from opal.tests.test_patient_lists import TaggingTestPatientList # flake8: noqa

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


class EpisodeListTemplateViewTestCase(BaseViewTestCase):

    def test_episode_list_view(self):
        url = reverse("episode_list_template_view", kwargs=dict(tag="eater", subtag="herbivore"))
        request = self.get_request(url)
        view = views.EpisodeListTemplateView()
        view.request = request
        context_data = view.get_context_data(tag="eater", subtag="herbivore")
        column_names = [i["name"] for i in context_data["columns"]]
        self.assertEqual(column_names, ["demographics"])
        self.should_200(views.EpisodeListTemplateView, request)

    def test_get_column_context_no_list(self):
        view = views.EpisodeListTemplateView()
        ctx = view.get_column_context(tag='notarealthing')
        self.assertEqual([], ctx)


class PatientDetailTemplateViewTestCase(BaseViewTestCase):

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
