"""
Unittests fror opal.core.test_runner
"""
import ffs
from mock import MagicMock, patch

from opal.core.test import OpalTestCase

from opal.core import test_runner

class RunPyTestsTestCase(OpalTestCase):

    @patch('subprocess.check_call')
    def test_run_tests(self, check_call):
        mock_args = MagicMock(name="args")
        mock_args.userland_here = ffs.Path('.')
        mock_args.coverage = False
        mock_args.test = None
        test_runner._run_py_tests(mock_args)
        check_call.assert_called_once_with(['python', 'runtests.py'])


class RunJSTestsTestCase(OpalTestCase):
    pass


class RunTestsTestCase(OpalTestCase):
    pass
