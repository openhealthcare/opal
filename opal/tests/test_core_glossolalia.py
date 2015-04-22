"""
Unittests for opal.core.glossolalia
"""
import json 

from django.test import TestCase
from mock import patch

from opal.core import glossolalia

class AdmitTestCase(TestCase):
    @patch('opal.core.glossolalia._send_upstream_message')
    def test_admit_not_integratng(self, sender):
        with patch('opal.core.glossolalia.INTEGRATING', new=False):
            admit = glossolalia.admit(None)
            self.assertEqual(None, admit) # Mostly a proxy for "Does this stacktrace?"
            self.assertFalse(sender.called)
            
    @patch('opal.core.glossolalia._send_upstream_message')
    def test_admit_calls_send_upstream(self, sender):
        with patch('opal.core.glossolalia.INTEGRATING', new=True):
            admit = glossolalia.admit({})
            self.assertEqual('admit', sender.call_args[0][0])
            self.assertEqual({}, json.loads(sender.call_args[0][1]['data'])['episode'])


class DischargeTestCase(TestCase):            
    @patch('opal.core.glossolalia._send_upstream_message')
    def test_admit_not_integratng(self, sender):
        with patch('opal.core.glossolalia.INTEGRATING', new=False):
            admit = glossolalia.discharge(None)
            self.assertEqual(None, admit) # Mostly a proxy for "Does this stacktrace?"
            self.assertFalse(sender.called)
            
    @patch('opal.core.glossolalia._send_upstream_message')
    def test_admit_calls_send_upstream(self, sender):
        with patch('opal.core.glossolalia.INTEGRATING', new=True):
            admit = glossolalia.discharge({})
            self.assertEqual('discharge', sender.call_args[0][0])
            self.assertEqual({}, json.loads(sender.call_args[0][1]['data'])['episode'])


            
class ChangeTestCase(TestCase):
    @patch('opal.core.glossolalia._send_upstream_message')
    def test_admit_not_integratng(self, sender):
        with patch('opal.core.glossolalia.INTEGRATING', new=False):
            admit = glossolalia.change(None, None)
            self.assertEqual(None, admit) # Mostly a proxy for "Does this stacktrace?"
            self.assertFalse(sender.called)
            
    @patch('opal.core.glossolalia._send_upstream_message')
    def test_admit_calls_send_upstream(self, sender):
        with patch('opal.core.glossolalia.INTEGRATING', new=True):
            admit = glossolalia.change({}, {'foo': 'bar'})
            self.assertEqual('change', sender.call_args[0][0])
            self.assertEqual('bar', json.loads(sender.call_args[0][1]['data'])['post']['foo'])
