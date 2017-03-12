"""
Unittests for opal.core.application
"""
from mock import patch, MagicMock

from opal.core.test import OpalTestCase

from opal.core import application

class OpalApplicationTestCase(OpalTestCase):

    def setUp(self):
        class App(application.OpalApplication):
            javascripts = ['test.js']
            styles = ['app.css']

        self.app = App

    def test_get_core_javascripts(self):
        expected = [
            "js/opal/controllers_module.js",
            "js/opal/controllers/patient_list_redirect.js",
            "js/opal/controllers/patient_list.js",
            "js/opal/controllers/patient_detail.js",
            "js/opal/controllers/hospital_number.js",
            "js/opal/controllers/add_episode.js",
            "js/opal/controllers/edit_item.js",
            "js/opal/controllers/edit_teams.js",
            "js/opal/controllers/delete_item_confirmation.js",
            "js/opal/controllers/account.js",
            "js/opal/controllers/discharge.js",
            "js/opal/controllers/undischarge.js",
            "js/opal/controllers/copy_to_category.js",
            "js/opal/controllers/keyboard_shortcuts.js",
            "js/opal/controllers/patient_access_log.js"
        ]
        self.assertEqual(
            expected,
            self.app.get_core_javascripts('opal.controllers'))

    def test_get_javascripts(self):
        self.assertEqual(['test.js'], self.app.get_javascripts())

    def test_get_menu_items(self):
        self.assertEqual(
            [],
            application.OpalApplication.get_menu_items())

    def test_get_menu_items_takes_user(self):
        self.assertEqual(
            [],
            application.OpalApplication.get_menu_items(user=self.user))

    def test_get_styles(self):
        self.assertEqual(['app.css'], self.app.get_styles())

    @patch("opal.core.application.inspect.getfile")
    def test_directory(self, getfile):
        getfile.return_value = "/"
        self.assertEqual(application.OpalApplication.directory(), "/")


class GetAppTestCase(OpalTestCase):

    @patch('opal.core.application.OpalApplication.__subclasses__')
    def test_get_app(self, subclasses):
        mock_app = MagicMock('Mock App')
        subclasses.return_value = [mock_app]
        self.assertEqual(mock_app, application.get_app())


class GetAllComponentsTestCase(OpalTestCase):

    @patch('opal.core.application.OpalApplication.__subclasses__')
    @patch('opal.core.plugins.OpalPlugin.list')
    def test_get_app(self, plugins, subclasses):
        mock_app = MagicMock('Mock App')
        plugin = MagicMock()
        plugins.return_value = [plugin]
        subclasses.return_value = [mock_app]
        self.assertEqual(
            [plugin, mock_app], list(application.get_all_components())
        )
