"""
Unittests for opal.templatetags.menus
"""
from django.template import Context
from mock import MagicMock

from opal.core import test

from opal.templatetags import menus

class MenuTestCase(test.OpalTestCase):

    def test_menu_passes_through_classes(self):
        ctx = menus.menu(Context({'user': MagicMock(name='User')}), 'myclass')
        self.assertEqual('myclass', ctx['classes'])
