"""
Unittests fror opal.core.test_runner
"""
import ffs
from mock import MagicMock, patch, call

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

    @patch('subprocess.check_call')
    def test_run_tests_with_test_arg(self, check_call):
        mock_args = MagicMock(name="args")
        mock_args.userland_here = ffs.Path('.')
        mock_args.coverage = False
        mock_args.test = 'opal.tests.foo'
        test_runner._run_py_tests(mock_args)
        check_call.assert_called_once_with(['python', 'runtests.py', 'opal.tests.foo'])

    @patch('subprocess.check_call')
    def test_run_tests_with_coverage(self, check_call):
        mock_args = MagicMock(name="args")
        mock_args.userland_here = ffs.Path('.')
        mock_args.coverage = True
        mock_args.test = None
        test_runner._run_py_tests(mock_args)
        calls = [
            call(['coverage', 'run', 'runtests.py']),
            call(['coverage', 'html'])
        ]

        check_call.assert_has_calls(calls)

    @patch('subprocess.check_call')
    @patch.object(test_runner, '_has_file')
    def test_run_tests_for_app_with_coverage(self, has_file, check_call):
        mock_args = MagicMock(name="args")
        mock_args.userland_here = ffs.Path('.')
        mock_args.coverage = True
        mock_args.test = None

        has_file.side_effect = lambda a, b: b == 'manage.py'

        test_runner._run_py_tests(mock_args)
        calls = [
            call(['coverage', 'run', 'manage.py', 'test']),
            call(['coverage', 'html'])
        ]

        check_call.assert_has_calls(calls)

    @patch('subprocess.check_call')
    @patch.object(test_runner, '_has_file')
    def test_run_tests_for_app_with_test(self, has_file, check_call):
        mock_args = MagicMock(name="args")
        mock_args.userland_here = ffs.Path('.')
        mock_args.coverage = False
        mock_args.test = 'foo.tests.bar'

        has_file.side_effect = lambda a, b: b == 'manage.py'

        test_runner._run_py_tests(mock_args)
        check_call.assert_called_with(['python', 'manage.py', 'test', 'foo.tests.bar'])

    @patch.object(test_runner, '_has_file')
    @patch.object(test_runner, 'write')
    @patch.object(test_runner.sys, 'exit')
    def test_run_tests_for_unknown_config(self, sysexit, writer, has_file):
        mock_args = MagicMock(name="args")
        mock_args.userland_here = ffs.Path('.')
        mock_args.coverage = False
        mock_args.test = None

        has_file.return_value = False

        test_runner._run_py_tests(mock_args)
        writer.assert_any_call("\n\nCripes!\n")
        sysexit.assert_called_with(1)


class RunJSTestsTestCase(OpalTestCase):
    pass


class RunTestsTestCase(OpalTestCase):
    pass
