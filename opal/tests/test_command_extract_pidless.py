"""
Unittests for opal.management.commands.extract_pidless
"""
from mock import patch

from opal.core.test import OpalTestCase

from opal.management.commands import extract_pidless as pidless

class CommandTestCase(OpalTestCase):

    def test_handle(self):
        c = pidless.Command()
        with patch.object(c.stdout, 'write'):
            opts = dict(exclude=[], format='json')
            self.assertEqual(None, c.handle(**opts))
