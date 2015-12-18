"""
Unittests for opal.views
"""
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


class EpisodeListTemplateViewTestCase(BaseViewTestCase):

    def test_episode_template_view(self):
        request = self.get_request('/episodetemplate')
        self.should_200(views.EpisodeListTemplateView, request)

class PatientDetailTemplateViewTestCase(BaseViewTestCase):

    def test_microhaem_template_view(self):
        request = self.get_request('/patient_detail_template')
        self.should_200(views.PatientDetailTemplateView, request)

class BannedViewTestCase(BaseViewTestCase):
    def test_banned_view(self):
        request = self.get_request('/banned_passwords')
        self.should_200(views.BannedView, request)
