from django.test import TestCase
from opal.templatetags.opalplugins import sort_menu_items

class MenuItemOrderingTest(TestCase):
    def test_with_fields_some_with_index(self):
        td = [
            dict(display="a", index=10),
            dict(display="b", index=10),
            dict(display="c", index=9),
            dict(display="d"),
        ]
        self.assertEqual(sort_menu_items(td), [td[2], td[0], td[1], td[3]])
