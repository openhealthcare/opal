"""
Unittests for the opal.core.tagging module
"""
from opal.core.test import OpalTestCase

from opal.tests import test_patient_lists

from opal.core import tagging


class ParentTestCase(OpalTestCase):
    def test_has_parent(self):
        self.assertEqual('eater', tagging.parent('herbivore'))

    def test_is_parent(self):
        self.assertEqual(None, tagging.parent('eater'))

    def test_parentless(self):
        self.assertEqual(None, tagging.parent('carnivore'))
