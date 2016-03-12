"""
Unittests for opal.core.detail
"""
from opal.core.test import OpalTestCase

from opal.core import detail


class View2(detail.PatientDetailView):
    order = 2

class View3(detail.PatientDetailView):
    order = 3

    @classmethod
    def visible_to(klass, user):
        return False

class View1(detail.PatientDetailView):
    order = 1


class PatientDetailViewTestCase(OpalTestCase):

    def test_default_order(self):
        self.assertEqual(None, detail.PatientDetailView.order)

    def test_ordering(self):
        self.assertEqual([View1, View2, View3], detail.PatientDetailView.list())

    def test_for_user(self):
        views = list(detail.PatientDetailView.for_user(self.user))
        self.assertEqual([View1, View2], views)

    def test_visible_to(self):
        self.assertTrue(View1.visible_to(self.user))
        self.assertFalse(View3.visible_to(self.user))
