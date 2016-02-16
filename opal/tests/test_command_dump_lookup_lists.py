"""
Unittests for opal.management.commands.dump_lookup_lists
"""
from mock import patch

from opal.core.test import OpalTestCase

from opal.management.commands import dump_lookup_lists as dll

class CreateSingletonsTestCase(OpalTestCase):
    def test_handle(self):
        c = dll.Command()
        with patch.object(c.stdout, 'write') as writer:
            c.handle()
            self.assertEqual(1, writer.call_count)
