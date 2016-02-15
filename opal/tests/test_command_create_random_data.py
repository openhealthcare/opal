"""
Unittests for opal.management.commands.create_random_data
"""
from mock import patch, MagicMock

from opal.core.test import OpalTestCase

from opal.management.commands import create_random_data as crd

class StringGeneratorTestCase(OpalTestCase):
    def test_string_generator(self):
        mock_field = MagicMock(name='Mock Field')
        mock_field.max_length = 30
        frist, last = crd.string_generator(mock_field).split()
        self.assertIn(frist, crd.adjectives)
        self.assertIn(last, crd.nouns)
