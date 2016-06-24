"""
Unittests for opal.utils
"""
from django.test import TestCase
from django.db.models import ForeignKey, CharField

from opal import utils

class StringportTestCase(TestCase):

    def test_import(self):
        import collections
        self.assertEqual(collections, utils.stringport('collections'))


class ItersubclassesTestCase(TestCase):
    def test_tree_structure(self):
        class A(object):
            pass

        class B(A):
            pass

        class C(B, utils.AbstractBase):
            pass

        class D(C):
            pass

        results = {i for i in utils._itersubclasses(A)}
        self.assertEqual(results, set([B, D]))


class FindTemplateTestCase(TestCase):

    def test_find_template_first_exists(self):
        self.assertEqual('base.html',
                         utils.find_template(['base.html', 'baser.html', 'basest.html']))

    def test_find_template_one_exists(self):
        self.assertEqual('base.html',
                         utils.find_template(['baser.html', 'base.html', 'basest.html']))

    def test_find_template_none_exists(self):
        self.assertEqual(None, utils.find_template(['baser.html', 'basest.html']))
