from opal.core.test import OpalTestCase
from opal.templatetags.opal_string_utils import underscore_to_spaces


class UnderscoreToSpacesTestCase(OpalTestCase):
    def test_underscore_to_spaces(self):
        self.assertEqual(
            "hello there",
            underscore_to_spaces("hello_there")
        )
