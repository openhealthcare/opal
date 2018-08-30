"""
Unittests for opal.utils
"""
import sys

from django.test import TestCase
from django.db.models import ForeignKey, CharField
from mock import patch

from opal.core import exceptions
from opal.core.test import OpalTestCase

from opal import utils

class StringportTestCase(TestCase):

    def test_import(self):
        import collections
        self.assertEqual(collections, utils.stringport('collections'))

    def test_import_no_period(self):
        with self.assertRaises(ImportError):
            utils.stringport('wotcha')

    def test_import_perioded_thing(self):
        self.assertEqual(TestCase, utils.stringport('django.test.TestCase'))

    def test_empty_name_is_valueerror(self):
        with self.assertRaises(ValueError):
            utils.stringport('')


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

    def test_when_called_with_type(self):
        expected = type.__subclasses__(type)
        for s in expected:
            self.assertIn(s, list(utils._itersubclasses(type)))


class FindTemplateTestCase(TestCase):

    def test_find_template_first_exists(self):
        self.assertEqual('base.html',
                         utils.find_template(['base.html', 'baser.html', 'basest.html']))

    def test_find_template_one_exists(self):
        self.assertEqual('base.html',
                         utils.find_template(['baser.html', 'base.html', 'basest.html']))

    def test_find_template_none_exists(self):
        self.assertEqual(None, utils.find_template(['baser.html', 'basest.html']))


class WriteTestCase(OpalTestCase):

    def test_write(self):
        with patch.object(utils, 'sys') as mocksys:
            mocksys.argv = ['not', 'te$targs']
            utils.write('this')
            mocksys.stdout.write.assert_called_with('this\n')


class RemoveKeysTestCase(OpalTestCase):

    def test_leaves_other_keys(self):
        d = dict(hello='world')
        removed = utils.remove_keys(d, 'goodbye')
        self.assertIn('hello', removed.keys())

    def test_removes_key(self):
        d = dict(hello='world', goodbye='cruel world')
        removed = utils.remove_keys(d, 'goodbye')
        self.assertNotIn('goodbye', removed.keys())
        self.assertIn('hello', removed.keys())

    def test_removes_multiple_keys(self):
        d = dict(hello='world', goodbye='cruel world', donna='lee')
        removed = utils.remove_keys(d, 'goodbye', 'donna')
        self.assertNotIn('goodbye', removed.keys())
        self.assertNotIn('donna', removed.keys())
        self.assertIn('hello', removed.keys())

    def test_removes_recursively(self):
        d = dict(greetings=dict(hello='world'))
        removed = utils.remove_keys(d, 'hello')
        self.assertIn('greetings', removed.keys())
        self.assertNotIn('hello', removed['greetings'].keys())

    def test_removes_from_list_of_dicts_recursively(self):
        d = dict(
            greetings=[
                dict(hello='world'),
                dict(hello='London'),
                dict(hello='friends')
            ]
        )
        removed = utils.remove_keys(d, 'hello')
        self.assertIn('greetings', removed.keys())
        self.assertNotIn('hello', removed['greetings'][0].keys())
        self.assertNotIn('hello', removed['greetings'][1].keys())
        self.assertNotIn('hello', removed['greetings'][2].keys())

    def test_no_keys(self):
        d = dict(greetings=dict(hello='world'))
        removed = utils.remove_keys(d)
        self.assertEqual(d, removed)


class TestRemoveEmptyListsTestCase(OpalTestCase):

    def test_removes_empty_lists(self):
        data = {'key': [], 'lock': [11]}
        result = utils.remove_empty_lists(data)
        self.assertEqual({'lock': [11]}, result)

    def test_removes_empty_lists_recursively(self):
        data = {'key': [], 'lock': [11], 'what': {
            'is': [],
            'this': 'thing',
            'called': {}
        }}
        result = utils.remove_empty_lists(data)
        self.assertEqual({'lock': [11], 'what': {'this': 'thing', 'called': {}}}, result)
