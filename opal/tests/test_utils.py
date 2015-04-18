from django.test import TestCase
from django.db.models import ForeignKey, CharField

from opal.utils import stringport

class StringportTestCase(TestCase):

    def test_import(self):
        import collections
        self.assertEqual(collections, stringport('collections'))

