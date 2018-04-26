"""
Unittests for import command
"""
from mock import MagicMock

from opal.core.test import OpalTestCase

from opal.management.commands import load

class LoadTestCase(OpalTestCase):

    def test_add_arguments(self):
        c = load.Command()
        parser = MagicMock()
        c.add_arguments(parser)
        parser.add_argument.assert_any_call(
            '--patient', '-p',
            dest='patient_file',
            help='Path to file containing a patient',
            default=None
        )
