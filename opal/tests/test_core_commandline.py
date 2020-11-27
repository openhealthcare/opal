"""
Unittests for opal.core.commandline
"""
import os
import sys

from unittest.mock import patch, MagicMock

from opal.core.test import OpalTestCase

from opal.core import commandline


class FindApplicationNameTestCase(OpalTestCase):

    @patch('ffs.Path.__bool__')
    @patch('ffs.Path.__nonzero__')
    @patch('ffs.Path.ls')
    @patch('ffs.Path.is_dir')
    def test_settings_exists(self, is_dir, ls, nz, bl):
        is_dir.return_value = True
        ls.side_effect = [
            [
                commandline.USERLAND_HERE/'opalapp',
                commandline.USERLAND_HERE/'notanapp'
            ]
        ]
        # We need both of these to make sure our tests run properly on Pythons 2&3
        nz.return_value = True
        bl.return_value = True

        name = commandline.find_application_name()
        self.assertEqual('opalapp', name)

    def test_not_found(self):
        with patch.object(commandline.sys, 'exit') as exiter:
            commandline.find_application_name()
            exiter.assert_called_with(1)


@patch('django.setup')
@patch.object(commandline, 'find_application_name')
@patch.dict(commandline.os.environ,{'mytemp':'mytemp'}, clear=True)
class SetupDjangoTestCase(OpalTestCase):

    def test_settings_module(self, name, setup):

        name.return_value = 'testapp'
        @commandline.setup_django
        def go():
            pass

        go()

        self.assertEqual(
            commandline.os.environ['DJANGO_SETTINGS_MODULE'],
            'testapp.settings'
        )

    def test_setup_called(self, name, setup):

        name.return_value = 'testapp'
        @commandline.setup_django
        def go():
            pass

        go()

        setup.assert_called_once_with()

    def test_sys_path_adds_dot(self, name, setup):
        with patch.object(commandline.sys, 'path', []):

            name.return_value = 'testapp'
            @commandline.setup_django
            def go():
                pass

            go()

            self.assertIn('.', commandline.sys.path)

    def test_sys_path_only_adds_dot_once(self, name, setup):
        with patch.object(commandline.sys, 'path', []):

            commandline.sys.path.append('.')
            name.return_value = 'testapp'
            @commandline.setup_django
            def go():
                pass

            go()

            self.assertEqual(1, len([p for p in commandline.sys.path if p == '.']))


class StartprojectTestCase(OpalTestCase):

    def test_startproject(self):
        mock_args = MagicMock(name='Mock Args')
        mock_args.name = 'projectname'
        with patch.object(commandline.scaffold_utils, 'start_project') as sp:
            commandline.startproject(mock_args)
            sp.assert_called_with('projectname', commandline.USERLAND_HERE)


class StartpluginTestCase(OpalTestCase):

    def test_startplugin(self):
        mock_args = MagicMock(name='Mock Args')
        mock_args.name = 'pluginname'
        with patch.object(commandline.scaffold_utils, 'start_plugin') as sp:
            commandline.startplugin(mock_args)
            sp.assert_called_with('pluginname', commandline.USERLAND_HERE)


class TestTestCase(OpalTestCase):

    def test_test(self):
        mock_args = MagicMock(name='Mock Args')
        with patch.object(commandline.test_runner, 'run_tests') as rt:
            commandline.test(mock_args)
            mock_args_call = rt.call_args[0][0]
            self.assertTrue(mock_args_call.userland_here.endswith("opal"),
                            "Not running tests from root directory")
            self.assertTrue(mock_args_call.opal_location.endswith("opal"))
            rt.assert_called_with(mock_args)


@patch('subprocess.check_output')
@patch('subprocess.check_call')
@patch('os.system')
class CheckoutTestCase(OpalTestCase):

    def test_check_for_uncommitted(self, os, check_call, check_output):
        check_output.return_value = ""
        self.assertEqual(0, commandline.check_for_uncommitted())

    def test_check_for_uncommitted_with_changes(self, os, check_call, check_output):
        check_output.return_value = "' M opal/tests/test_core_commandline.py\n'"
        self.assertEqual(41, commandline.check_for_uncommitted())

    def test_get_requirements(self, os, check_call, check_output):
        requirements = """
Django==1.9.1
-e git+https://github.com/openhealthcare/opal.git@v10.8.0#egg=opal
"""
        check_output.return_value = requirements
        r = commandline.get_requirements()
        expected = {
            'opal': 'v10.8.0'
        }
        self.assertEqual(expected, r)

    @patch('ffs.Path.ls')
    def test_checkout(self, ls, os, check_call, check_output):
        mock_args = MagicMock(name='Mock Args')
        ls.return_value = ['opal', 'someotherpackage']
        with patch.object(commandline, 'get_requirements') as reqs:
            with patch.object(commandline, 'write') as writer:
                reqs.return_value = {
                    'opal': 'v10.8.0'
                }
                commandline.checkout(mock_args)
                os.assert_any_call('git checkout v10.8.0')
                os.assert_any_call('python setup.py develop')
                writer.assert_any_call('checking out opal to v10.8.0')

    @patch('ffs.Path.ls')
    def test_checkout_clones_package(self, ls, os, check_call, check_output):
        mock_args = MagicMock(name='Mock Args')
        ls.return_value = ['opal', 'someotherpackage']
        with patch.object(commandline, 'get_requirements') as reqs:
            with patch.object(commandline, 'write') as writer:
                reqs.return_value = {
                    'opal'          : 'v10.8.0',
                    'missingpackage': '1.0'
                }
                commandline.checkout(mock_args)
                writer.assert_any_call('missingpackage is missing')

    @patch('ffs.Path.ls')
    def test_checkout_with_uncommitted(self, ls, os, check_call, check_output):
        mock_args = MagicMock(name='Mock Args')
        ls.return_value = ['opal']
        with patch.object(commandline, 'get_requirements') as reqs:
            with patch.object(commandline, 'write') as writer:
                with patch.object(commandline, 'check_for_uncommitted') as checker:
                    reqs.return_value = {
                        'opal'          : 'v10.8.0',
                    }
                    checker.return_value = 41
                    commandline.checkout(mock_args)
                    writer.assert_any_call('We have uncommitted changes in opal')
                    writer.assert_any_call('Abandonning attempt to check out to requirements.txt')



class ServeTestCase(OpalTestCase):

    def test_serve(self):
        with patch.object(commandline.management, 'call_command') as call:
            with patch.object(commandline, 'find_application_name') as name:
                name.return_value = 'testapp'

                mock_args = MagicMock(name='Mock args')
                mock_args.addrport=['localhost:8000']
                commandline.serve(mock_args)
                call.assert_called_once_with('runserver', 'localhost:8000', '--traceback')


class ParseArgsTestCase(OpalTestCase):

    def test_parse_args(self):
        with patch.object(commandline.sys, 'exit') as exiter:
            with patch.object(commandline, 'test') as tester:
                commandline.parse_args(['test', 'py'])
                exiter.assert_called_with(0)



class MainTestCase(OpalTestCase):

    def test_main(self):
        with patch.object(commandline, 'parse_args') as pa:
            commandline.main()
            pa.assert_called_with(sys.argv[1:])
