"""
Unittests for opal.views
"""
from django import http
from mock import patch, MagicMock
from opal.core.test import OpalTestCase
from opal import models

from opal import views

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


class BannedViewTestCase(BaseViewTestCase):
    def test_banned_view(self):
        request = self.get_request('/banned_passwords')
        self.should_200(views.BannedView, request)
