"""
Unittests for opal.core.application
"""
import os
import copy

from django.contrib.auth.models import AnonymousUser
from unittest.mock import patch, MagicMock

from opal.core.test import OpalTestCase

from opal.core import application, menus

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
            "js/opal/controllers/edit_item.js",
            "js/opal/controllers/edit_teams.js",
            "js/opal/controllers/delete_item_confirmation.js",
            "js/opal/controllers/keyboard_shortcuts.js",
            "js/opal/controllers/patient_access_log.js",
            "js/opal/controllers/lookup_list_reference.js"
        ]
        self.assertEqual(
            expected,
            self.app.get_core_javascripts('opal.controllers'))

    def test_get_core_javascripts_updating_side_effects(self):
        controllers = self.app.get_core_javascripts('opal.controllers')
        controllers_original = copy.copy(controllers)
        controllers.append('not/a/javascript/file')
        self.assertFalse(
            'not/a/javascriptfile' in self.app.get_core_javascripts('opal.controllers')
        )
        self.assertEqual(controllers_original, self.app.get_core_javascripts('opal.controllers'))

    def test_get_javascripts(self):
        self.assertEqual(['test.js'], self.app.get_javascripts())

    def test_get_javascripts_updating_side_effects(self):
        scripts = self.app.get_javascripts()
        scripts_original = copy.copy(scripts)
        scripts.append('lolcats.js')
        self.assertFalse('lolcats.js' in self.app.get_javascripts())
        self.assertEqual(scripts_original, self.app.get_javascripts())

    def test_get_menu_items(self):
        self.assertEqual(
            application.OpalApplication.menuitems,
            application.OpalApplication.get_menu_items()
        )

    def test_get_menu_items_for_user(self):
        class MenuItemIncluded(menus.MenuItem):
            pass

        class MenuItemNotIncluded(menus.MenuItem):
            def for_user(self, user):
                return False

        menu_item_included = MenuItemIncluded()
        menu_item_not_included = MenuItemNotIncluded()

        self.app.menuitems = [
                    menu_item_included, menu_item_not_included
                ]

        self.assertEqual(
            [menu_item_included],
            list(self.app.get_menu_items())
        )

    def test_get_menu_items_includes_logout_for_authenticated_users(self):
        user = self.user
        menuitems = application.OpalApplication.get_menu_items(user=user)
        self.assertEqual(1, len([m for m in menuitems if m.icon == 'fa-sign-out']))

    def test_get_menu_items_includes_admin_for_superuser(self):
        user = self.user
        user.is_staff = True
        menuitems = application.OpalApplication.get_menu_items(user=user)
        self.assertEqual(1, len([m for m in menuitems if m.href == '/admin/']))

    def test_get_menu_items_empty_for_anonymous_user(self):
        user = AnonymousUser()
        menuitems = application.OpalApplication.get_menu_items(user=user)
        self.assertEqual([], menuitems)

    def test_get_menu(self):
        menu = application.OpalApplication.get_menu()
        self.assertIsInstance(menu, menus.Menu)

    def test_get_styles(self):
        self.assertEqual(['app.css'], self.app.get_styles())

    def test_get_styles_updating_side_effects(self):
        styles = self.app.get_styles()
        styles_original = copy.copy(styles)
        styles.append('IE6.polyfills.css')
        self.assertFalse('IE6.polyfills.css' in self.app.get_styles())
        self.assertEqual(styles_original, self.app.get_styles())

    @patch("opal.core.application.inspect.getfile")
    def test_directory(self, getfile):
        getfile.return_value = "/"
        self.assertEqual(application.OpalApplication.directory(), os.path.abspath(os.sep))

    @patch('opal.core.application.get_all_components')
    def test_opal_angular_deps(self, get_all_components):
        fake_application = MagicMock()
        fake_application.angular_module_deps = ["upstream.dependency"]
        get_all_components.return_value = [
            fake_application
        ]
        self.assertEqual(
            application.OpalApplication.get_all_angular_module_deps(),
            ["upstream.dependency"]
        )


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
