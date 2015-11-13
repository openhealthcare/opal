"""
Unittests for opal.core.application
"""
from django.test import TestCase
from mock import patch, MagicMock

from opal.core import application

class OpalApplicationTestCase(TestCase):
    def setUp(self):
        class App(application.OpalApplication):
            flow_module = 'opal.tests.flows'

        self.app = App

    @patch('opal.core.plugins.plugins')
    def test_flows_no_flow_module(self, subclasses):
        class App(application.OpalApplication): pass
        subclasses.return_value = []
        self.assertEqual({}, App.flows())

    @patch('opal.core.plugins.plugins')
    @patch('opal.core.application.stringport')
    def test_flows(self, stringport, pluginsubs):
        pluginsubs.return_value = []
        mock_flows = MagicMock(name='flow module')
        mock_flows.flows = {'default': { 'enter': '', 'exit': '' } }
        stringport.return_value = mock_flows

        flows = self.app.flows()

        stringport.assert_called_with('opal.tests.flows')
        self.assertEqual(mock_flows.flows, flows)


class GetAppTestCase(TestCase):
    @patch('opal.core.application.OpalApplication.__subclasses__')
    def test_get_app(self, subclasses):
        mock_app = MagicMock('Mock App')
        subclasses.return_value = [mock_app]
        self.assertEqual(mock_app, application.get_app())
