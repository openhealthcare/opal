"""
Unittests for opal.core.menus
"""
import warnings

from mock import patch, MagicMock

from opal.core.test import OpalTestCase

from opal.core import menus


class MenuItemTestCase(OpalTestCase):

    def test_sets_properties__if_empty(self):
        item = menus.MenuItem()
        self.assertEqual(item.template_name, "")
        self.assertEqual(item.activepattern, "")
        self.assertEqual(item.href, "")
        self.assertEqual(item.icon, "")
        self.assertEqual(item.display, "")
        self.assertEqual(item.index, 100)

    def test_sets_kwargs(self):
        item = menus.MenuItem(
            template_name='menu.html',
            activepattern='/thing',
            href='/thing/',
            icon='fa-thing',
            display="Thing",
            index=0
        )
        self.assertEqual(item.template_name, 'menu.html')
        self.assertEqual(item.activepattern, '/thing')
        self.assertEqual(item.href, '/thing/')
        self.assertEqual(item.icon, 'fa-thing')
        self.assertEqual(item.display, "Thing")
        self.assertEqual(item.index, 0)

    def test_repr(self):
        item = menus.MenuItem(href="/wat/")
        self.assertEqual("<Opal MenuItem href: '/wat/'>", item.__repr__())


@patch('opal.core.plugins.OpalPlugin.list')
@patch('opal.core.application.get_app')
class MenuTestCase(OpalTestCase):

    def setUp(self):
        self.app = MagicMock(name='App')
        self.app.get_menu_items.return_value = []

    def test_empty_items(self, get_app, plugin_list):
        get_app.return_value = self.app
        plugin_list.return_value = []
        menu = menus.Menu(user=self.user)
        self.assertEqual([], menu.items)

    def test_sets_items_from_app(self, get_app, plugin_list):
        get_app.return_value = self.app
        plugin_list.return_value = []
        menu_items = [menus.MenuItem()]
        self.app.get_menu_items.return_value = menu_items
        menu = menus.Menu(user=self.user)
        self.assertEqual(menu_items, menu.items)

    def test_sets_items_from_plugin(self, get_app, plugin_list):
        get_app.return_value = self.app
        menu_items = [menus.MenuItem()]
        mock_plugin = MagicMock(name='Plugin')
        mock_plugin.menuitems = menu_items
        plugin_list.return_value = [mock_plugin]
        menu = menus.Menu(user=self.user)
        self.assertEqual(menu_items, menu.items)

    def test_sets_items_from_app_dict(self, get_app, plugin_list):
        with warnings.catch_warnings(record=True):
            get_app.return_value = self.app
            plugin_list.return_value = []
            menu_items = [{'display': 'Display Name'}]
            self.app.get_menu_items.return_value = menu_items
            menu = menus.Menu(user=self.user)
            self.assertEqual('Display Name', menu.items[0].display)

    def test_sets_items_from_plugin_dict(self, get_app, plugin_list):
        with warnings.catch_warnings(record=True):
            get_app.return_value = self.app
            menu_items = [{'display': 'Display Name'}]
            mock_plugin = MagicMock(name='Plugin')
            mock_plugin.menuitems = menu_items
            plugin_list.return_value = [mock_plugin]
            menu = menus.Menu(user=self.user)
            self.assertEqual('Display Name', menu.items[0].display)


    def test_iter_sorts(self, get_app, plugin_list):
        get_app.return_value = self.app
        plugin_list.return_value = []
        menu = menus.Menu(user=self.user)
        menu.items = [
            menus.MenuItem(href='/third', index=4),
            menus.MenuItem(href='/first', index=2),
            menus.MenuItem(href='/second', index=2),
        ]
        expected = [
            '/first',
            '/second',
            '/third'
        ]
        for i, item in enumerate(i for i in menu):
            self.assertEqual(expected[i], item.href)
