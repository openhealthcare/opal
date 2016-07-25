from opal.core.test import OpalTestCase
from opal.tests.models import DogOwner, HoundOwner


class TestForeignKeyOrFreeText(OpalTestCase):

    def test_unset_verbose_name(self):
        field = getattr(DogOwner, "dog")
        self.assertEqual(field.verbose_name, "dog")

    def test_set_verbose_name(self):
        field = getattr(HoundOwner, "dog")
        self.assertEqual(field.verbose_name, "hound")

    def test_set_max_length(self):
        field = getattr(HoundOwner, "dog")
        self.assertEqual(field.max_length, 255)
