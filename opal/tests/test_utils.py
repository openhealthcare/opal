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


class GetTestCase(OpalTestCase):

    def test_get_attribute(self):

        class A(object):
            request = 'Straight, no chaser'

        self.assertEqual('Straight, no chaser', utils.get(A, 'request'))

    def test_get_getter(self):

        class A(object):

            @classmethod
            def get_request(kls):
                return 'Straight, no chaser'

        self.assertEqual('Straight, no chaser', utils.get(A, 'request'))


    def test_get_default(self):

        class A(object):
            pass

        self.assertEqual(
            'In The Still Of The Night',
            utils.get(A, 'request', 'In The Still Of The Night')
        )

    def test_get_falsy_default(self):

        class A(object):
            pass

        self.assertEqual(False, utils.get(A, 'predicate', False))

    def test_get_none_default(self):

        class A(object):
            pass

        self.assertEqual(None, utils.get(A, 'predicate', None))

    def test_get_attribute_missing_no_default(self):

        class A(object):
            pass

        with self.assertRaises(AttributeError):
            utils.get(A, 'request')


    def test_get_attribute_and_getter(self):

        class A(object):
            request = "I've Got You Under My Skin"

            @classmethod
            def get_request(kls):
                return 'What Is This Thing Called Love'

        self.assertEqual('What Is This Thing Called Love', utils.get(A, 'request'))

    def test_too_many_args(self):
        with self.assertRaises(exceptions.SignatureError):
            utils.get(1,2,3,3)

    def test_too_few_args(self):
        with self.assertRaises(exceptions.SignatureError):
            utils.get(1)
