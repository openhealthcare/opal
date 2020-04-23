"""
Unittests for opal.core.menus
"""
import operator
import warnings

from unittest.mock import patch, MagicMock

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

    def test_for_user(self):
        item = menus.MenuItem(href="/wat/")
        self.assertTrue(item.for_user(self.user))

    def test_equality(self):
        item1 = menus.MenuItem(
            template_name='menu.html',
            activepattern='/item1',
            href='/item1/',
            icon='fa-item1',
            display="Item1",
            index=0
        )

        item1dup = menus.MenuItem(
            template_name='menu.html',
            activepattern='/item1',
            href='/item1/',
            icon='fa-item1',
            display="Item1",
            index=0
        )

        item2 = menus.MenuItem(
            template_name='menu.html',
            activepattern='/item2',
            href='/item2/',
            icon='fa-item2',
            display="Item2",
            index=0
        )

        self.assertTrue(item1 == item1)
        self.assertTrue(operator.eq(item1, item1))
        self.assertTrue(item1 == item1dup)
        self.assertTrue(operator.eq(item1, item1dup))
        self.assertTrue(item1dup == item1)
        self.assertTrue(operator.eq(item1dup, item1))
        self.assertTrue(item1 != item2)
        self.assertTrue(operator.ne(item1, item2))
        self.assertFalse(operator.ne(item1, item1dup))
        self.assertFalse(item1 == 1)
        self.assertFalse(1 == item2)
        self.assertTrue(1 != item2)
        self.assertTrue(item2 != 1)


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

    def test_excludes_items_from_app_if_for_user_is_false(
        self, get_app, plugin_list
    ):
        get_app.return_value = self.app
        plugin_list.return_value = []
        menu_item = menus.MenuItem()
        menu_items = [menu_item]
        self.app.menuitems = menu_items
        with patch.object(menu_item, "for_user") as for_user:
            for_user.return_value = False
            menu = menus.Menu(user=self.user)
            self.assertEqual([], menu.items)

    def test_sets_items_from_plugin(self, get_app, plugin_list):
        get_app.return_value = self.app
        menu_items = [menus.MenuItem()]
        mock_plugin = MagicMock(name='Plugin')
        mock_plugin.get_menu_items.return_value = menu_items
        plugin_list.return_value = [mock_plugin]
        menu = menus.Menu(user=self.user)
        self.assertEqual(menu_items, menu.items)

    def test_excludes_items_from_plugin_if_for_user_is_false(
        self, get_app, plugin_list
    ):
        get_app.return_value = self.app
        menu_item = menus.MenuItem()
        menu_items = [menu_item]
        mock_plugin = MagicMock(name='Plugin')
        mock_plugin.menuitems = menu_items
        plugin_list.return_value = [mock_plugin]
        with patch.object(menu_item, "for_user") as for_user:
            for_user.return_value = False
            menu = menus.Menu(user=self.user)
            self.assertEqual([], menu.items)

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
