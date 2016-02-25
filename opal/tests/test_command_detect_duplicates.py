"""
Unittests for opal.management.commands.detect_duplicates
"""
from mock import patch

from opal.core.test import OpalTestCase
from opal import models

from opal.management.commands import detect_duplicates as detector

class CommandTestCase(OpalTestCase):

    def setUp(self):
        self.patient = models.Patient.objects.create()

    def test_handle(self):
        c = detector.Command()
        with patch.object(c.stdout, 'write') as writer:
            c.handle()
            writer.assert_any_call('Duplicate detection starting...')
