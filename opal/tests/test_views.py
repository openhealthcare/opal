"""
Unittests for opal.views
"""
from mock import MagicMock
from opal.core.test import OpalTestCase
from opal import models
from django.core.urlresolvers import reverse
from opal import views
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


class BannedViewTestCase(BaseViewTestCase):
    def test_banned_view(self):
        request = self.get_request('/banned_passwords')
        self.should_200(views.BannedView, request)


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
