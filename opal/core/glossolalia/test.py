import json
from mock import patch, Mock

from django.test import TestCase
from django.core.urlresolvers import reverse

from opal.core import glossolalia
from opal.core.test import OpalTestCase
from opal.core.glossolalia import triggers
from opal.core.glossolalia.models import GlossolaliaSubscription
from opal import models as opal_models


class SubscriptionTest(OpalTestCase):

    def setUp(self):
        self.patient = opal_models.Patient.objects.create()

    def get_mock_request_obj(self, return_value):
        json_response = Mock(return_value=return_value)
        mock_response = Mock()
        mock_response.json = json_response
        return mock_response

    @patch("opal.core.glossolalia.triggers._send_upstream_message")
    def test_subscribe(self, mock_send):
        mock_response = self.get_mock_request_obj(return_value={"id": 1})
        mock_send.return_value = mock_response
        episode = opal_models.Episode.objects.create(patient=self.patient)
        triggers.subscribe(episode)
        self.assertTrue(mock_response.json.called)
        self.assertTrue(GlossolaliaSubscription.objects.filter(
            patient_id=self.patient.id,
            subscription_type=GlossolaliaSubscription.ALL_INFORMATION,
            gloss_id=1
        ).exists())

    @patch("opal.core.glossolalia.triggers._send_upstream_message")
    def test_unsubscribe(self, mock_send):
        mock_response = self.get_mock_request_obj(return_value={"id": 1})
        mock_send.return_value = mock_response
        episode = opal_models.Episode.objects.create(patient=self.patient)
        triggers.unsubscribe(episode)
        self.assertTrue(mock_response.json.called)
        self.assertTrue(GlossolaliaSubscription.objects.filter(
            patient_id=self.patient.id,
            subscription_type=GlossolaliaSubscription.CORE_DEMOGRAPHICS,
            gloss_id=1
        ).exists())

    def test_list_subscription(self):
        GlossolaliaSubscription.objects.create(
            patient=self.patient,
            subscription_type=GlossolaliaSubscription.CORE_DEMOGRAPHICS,
            gloss_id=1
        )
        url = reverse('glossolalia-list')
        self.assertStatusCode(url, 200)


class AdmitTestCase(TestCase):
    @patch('opal.core.glossolalia.triggers._send_upstream_message')
    def test_admit_not_integratng(self, sender):
        with patch('opal.core.glossolalia.triggers.INTEGRATING', new=False):
            admit = glossolalia.admit(None)
            self.assertEqual(None, admit) # Mostly a proxy for "Does this stacktrace?"
            self.assertFalse(sender.called)

    @patch('opal.core.glossolalia.triggers._send_upstream_message')
    def test_admit_calls_send_upstream(self, sender):
        with patch('opal.core.glossolalia.triggers.INTEGRATING', new=True):
            admit = glossolalia.admit({})
            self.assertEqual('admit', sender.call_args[0][0])
            self.assertEqual({}, json.loads(sender.call_args[0][1]['data'])['episode'])


class DischargeTestCase(TestCase):
    @patch('opal.core.glossolalia.triggers._send_upstream_message')
    def test_discharge_not_integratng(self, sender):
        with patch('opal.core.glossolalia.triggers.INTEGRATING', new=False):
            discharge = glossolalia.discharge(None)
            self.assertEqual(None, discharge) # Mostly a proxy for "Does this stacktrace?"
            self.assertFalse(sender.called)

    @patch('opal.core.glossolalia.triggers._send_upstream_message')
    def test_discharge_calls_send_upstream(self, sender):
        with patch('opal.core.glossolalia.triggers.INTEGRATING', new=True):
            discharge = glossolalia.discharge({})
            self.assertEqual('discharge', sender.call_args[0][0])
            self.assertEqual({}, json.loads(sender.call_args[0][1]['data'])['episode'])


class TransferTestCase(TestCase):
    @patch('opal.core.glossolalia.triggers._send_upstream_message')
    def test_transfer_not_integratng(self, sender):
        with patch('opal.core.glossolalia.triggers.INTEGRATING', new=False):
            transfer = glossolalia.transfer(None, None)
            self.assertEqual(None, transfer) # Mostly a proxy for "Does this stacktrace?"
            self.assertFalse(sender.called)

    @patch('opal.core.glossolalia.triggers._send_upstream_message')
    def test_transfer_calls_send_upstream(self, sender):
        with patch('opal.core.glossolalia.triggers.INTEGRATING', new=True):
            transfer = glossolalia.transfer({}, {'foo': 'bar'})
            self.assertEqual('transfer', sender.call_args[0][0])
            self.assertEqual('bar', json.loads(sender.call_args[0][1]['data'])['post']['foo'])


class ChangeTestCase(TestCase):
    @patch('opal.core.glossolalia.triggers._send_upstream_message')
    def test_change_not_integratng(self, sender):
        with patch('opal.core.glossolalia.triggers.INTEGRATING', new=False):
            change = glossolalia.change(None, None)
            self.assertEqual(None, change) # Mostly a proxy for "Does this stacktrace?"
            self.assertFalse(sender.called)

    @patch('opal.core.glossolalia.triggers._send_upstream_message')
    def test_change_calls_send_upstream(self, sender):
        with patch('opal.core.glossolalia.triggers.INTEGRATING', new=True):
            change = glossolalia.change({}, {'foo': 'bar'})
            self.assertEqual('change', sender.call_args[0][0])
            self.assertEqual('bar', json.loads(sender.call_args[0][1]['data'])['post']['foo'])

# test subscribe

# test unsubscribe

# test get list-api
