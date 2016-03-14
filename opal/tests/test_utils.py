from django.test import TestCase
from django.db.models import ForeignKey, CharField

from opal import utils

class StringportTestCase(TestCase):

    def test_import(self):
        import collections
        self.assertEqual(collections, utils.stringport('collections'))


class FindTemplateTestCase(TestCase):

    def test_find_template_first_exists(self):
        self.assertEqual('base.html',
                         utils.find_template(['base.html', 'baser.html', 'basest.html']))

    def test_find_template_one_exists(self):
        self.assertEqual('base.html',
                         utils.find_template(['baser.html', 'base.html', 'basest.html']))

    def test_find_template_none_exists(self):
        self.assertEqual(None, utils.find_template(['baser.html', 'basest.html']))
