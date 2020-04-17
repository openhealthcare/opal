"""
Unittests fror opal.core.test_runner
"""
import subprocess

import ffs
from unittest.mock import MagicMock, patch, call

from opal.core.test import OpalTestCase

from opal.core import test_runner

class RunPyTestsTestCase(OpalTestCase):

    @patch('subprocess.check_call')
    def test_run_tests(self, check_call):
        mock_args = MagicMock(name="args")
        mock_args.userland_here = ffs.Path('.')
        mock_args.coverage = False
        mock_args.test = None
        mock_args.failfast = False
        test_runner._run_py_tests(mock_args)
        check_call.assert_called_once_with(['python', 'runtests.py'])

    @patch('subprocess.check_call')
    @patch.object(test_runner.sys, 'exit')
    def test_run_tests_errors(self, exiter, check_call):
        mock_args = MagicMock(name="args")
        mock_args.userland_here = ffs.Path('.')
        mock_args.coverage = False
        mock_args.test = None
        mock_args.failfast = False
        check_call.side_effect = subprocess.CalledProcessError(None, None)
        test_runner._run_py_tests(mock_args)
        exiter.assert_called_once_with(1)

    @patch('subprocess.check_call')
    def test_run_tests_with_test_arg(self, check_call):
        mock_args = MagicMock(name="args")
        mock_args.userland_here = ffs.Path('.')
        mock_args.coverage = False
        mock_args.test = 'opal.tests.foo'
        mock_args.failfast = False
        test_runner._run_py_tests(mock_args)
        check_call.assert_called_once_with(['python', 'runtests.py', 'opal.tests.foo'])

    @patch('subprocess.check_call')
    def test_run_tests_with_coverage(self, check_call):
        mock_args = MagicMock(name="args")
        mock_args.userland_here = ffs.Path('.')
        mock_args.coverage = True
        mock_args.test = None
        mock_args.failfast = False
        test_runner._run_py_tests(mock_args)
        calls = [
            call(['coverage', 'run', 'runtests.py']),
            call(['coverage', 'html'])
        ]

        check_call.assert_has_calls(calls)

    @patch('subprocess.check_call')
    def test_run_tests_with_coverage_and_test_arg(self, check_call):
        mock_args = MagicMock(name="args")
        mock_args.userland_here = ffs.Path('.')
        mock_args.coverage = True
        mock_args.test = 'opal.tests.foo'
        mock_args.failfast = False
        test_runner._run_py_tests(mock_args)
        calls = [
            call(['coverage', 'run', 'runtests.py', 'opal.tests.foo']),
            call(['coverage', 'html'])
        ]

    @patch('subprocess.check_call')
    @patch.object(test_runner.sys, 'exit')
    def test_run_tests_with_coverage_errors(self, exiter, check_call):
        mock_args = MagicMock(name="args")
        mock_args.userland_here = ffs.Path('.')
        mock_args.coverage = True
        mock_args.test = None
        mock_args.failfast = False
        check_call.side_effect = [None, subprocess.CalledProcessError(None, None)]
        test_runner._run_py_tests(mock_args)
        self.assertEqual(2, check_call.call_count)
        exiter.assert_called_once_with(1)

    @patch('subprocess.check_call')
    @patch.object(test_runner, '_has_file')
    def test_run_tests_for_app_with_coverage(self, has_file, check_call):
        mock_args = MagicMock(name="args")
        mock_args.userland_here = ffs.Path('.')
        mock_args.coverage = True
        mock_args.failfast = False
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
        mock_args.failfast = False
        mock_args.test = 'foo.tests.bar'

        has_file.side_effect = lambda a, b: b == 'manage.py'

        test_runner._run_py_tests(mock_args)
        check_call.assert_called_with(['python', 'manage.py', 'test', 'foo.tests.bar'])

    @patch('subprocess.check_call')
    def test_run_tests_failfast(self, check_call):
        mock_args = MagicMock(name='args')
        mock_args.userland_here = ffs.Path('.')
        mock_args.coverage = False
        mock_args.test = False
        mock_args.failfast = True
        test_runner._run_py_tests(mock_args)
        check_call.assert_called_with(['python', 'runtests.py', '--failfast'])

    @patch.object(test_runner, '_has_file')
    @patch.object(test_runner, 'write')
    @patch.object(test_runner.sys, 'exit')
    def test_run_tests_for_unknown_config(self, sysexit, writer, has_file):
        mock_args = MagicMock(name="args")
        mock_args.userland_here = ffs.Path('.')
        mock_args.coverage = False
        mock_args.test = None
        mock_args.failfast = False

        has_file.return_value = False

        test_runner._run_py_tests(mock_args)
        writer.assert_any_call("\n\nCripes!\n")
        sysexit.assert_called_with(1)


class RunJSTestsTestCase(OpalTestCase):

    def setUp(self):
        self.TRAVIS = test_runner.TRAVIS

    def tearDown(self):
        test_runner.TRAVIS = self.TRAVIS

    @patch('subprocess.check_call')
    def test_run_tests(self, check_call):
        mock_args = MagicMock(name="args")
        mock_args.userland_here = ffs.Path('.')
        mock_args.coverage = False
        mock_args.test = None
        mock_args.failfast = False
        test_runner.TRAVIS = False
        test_runner._run_js_tests(mock_args)
        self.assertEqual(
            ['karma', 'start', 'config/karma.conf.js', '--single-run'],
            check_call.call_args[0][0]
        )

    @patch('subprocess.check_call')
    def test_run_tests_travis(self, check_call):
        mock_args = MagicMock(name="args")
        mock_args.userland_here = ffs.Path('.')
        mock_args.coverage = False
        mock_args.test = None
        mock_args.failfast = False
        test_runner.TRAVIS = True
        test_runner._run_js_tests(mock_args)
        self.assertEqual(
            [
                './node_modules/karma/bin/karma',
                'start',
                'config/karma.conf.js',
                '--single-run'
            ],
            check_call.call_args[0][0]
        )
        self.assertIn("OPAL_LOCATION", check_call.call_args[1]["env"])

        self.assertTrue(
            isinstance(check_call.call_args[1]["env"]["OPAL_LOCATION"], str)
        )

    @patch.object(test_runner.subprocess, 'check_call')
    def test_run_tests_failfast(self, check_call):
        mock_args = MagicMock(name="args")
        mock_args.userland_here = ffs.Path('.')
        mock_args.coverage = False
        mock_args.test = None
        mock_args.failfast = True
        test_runner.TRAVIS = False
        test_runner._run_js_tests(mock_args)
        self.assertEqual(
            [
                'karma',
                'start',
                'config/karma.conf.js',
                '--single-run',
                '--failfast'
            ],
            check_call.call_args[0][0]
        )

    @patch.object(test_runner.subprocess, 'check_call')
    @patch.object(test_runner.sys, 'exit')
    def test_generic_error_in_call(self, exiter, check_call):
        check_call.side_effect = subprocess.CalledProcessError(None, None)
        mock_args = MagicMock(name="args")
        test_runner._run_js_tests(mock_args)
        exiter.assert_called_with(1)

    @patch('subprocess.check_call')
    @patch.object(test_runner.sys, 'exit')
    @patch.object(test_runner, 'write')
    def test_oserror_in_call(self, writer, exiter, check_call):
        check_call.side_effect = OSError(2, 'No such file or directory')
        mock_args = MagicMock(name="args")
        test_runner._run_js_tests(mock_args)
        exiter.assert_called_with(1)
        writer.assert_any_call("We can't find the karma executable\n")


class RunTestsTestCase(OpalTestCase):

    @patch.object(test_runner, '_run_js_tests')
    @patch.object(test_runner, '_run_py_tests')
    def test_run_tests(self, py, js):
        mock_args = MagicMock(name='Args')
        mock_args.what = 'all'
        test_runner.run_tests(mock_args)
        py.assert_called_with(mock_args)
        js.assert_called_with(mock_args)

    @patch.object(test_runner, '_run_js_tests')
    @patch.object(test_runner, '_run_py_tests')
    def test_run_py_tests(self, py, js):
        mock_args = MagicMock(name='Args')
        mock_args.what = ['py']
        test_runner.run_tests(mock_args)
        py.assert_called_with(mock_args)
        self.assertEqual(0, js.call_count)
