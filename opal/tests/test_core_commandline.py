"""
Unittests for opal.core.commandline
"""
import sys

from mock import patch, MagicMock

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

        name = commandline._find_application_name()
        self.assertEqual('opalapp', name)

    def test_not_found(self):
        with patch.object(commandline.sys, 'exit') as exiter:
            commandline._find_application_name()
            exiter.assert_called_with(1)


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


@patch('subprocess.check_call')
@patch('os.system')
class ScaffoldTestCase(OpalTestCase):

    def test_scaffold(self, os, sub):
        mock_args = MagicMock(name='Mock Args')
        mock_args.app = 'opal'
        mock_args.dry_run = False
        with patch.object(commandline, '_find_application_name') as namer:
            namer.return_value = 'opal.tests'
            commandline.scaffold(mock_args)
            os.assert_any_call('python manage.py makemigrations opal --traceback ')
            os.assert_any_call('python manage.py migrate opal --traceback')

    def test_dry_run(self, os, sub):
        mock_args = MagicMock(name='Mock Args')
        mock_args.app = 'opal'
        mock_args.dry_run = True
        with patch.object(commandline, '_find_application_name') as namer:
            namer.return_value = 'opal.tests'
            commandline.scaffold(mock_args)
            os.assert_any_call('python manage.py makemigrations opal --traceback --dry-run')

    @patch('opal.models.EpisodeSubrecord.get_display_template')
    def test_episode_subrecord_no_display_template(self, episub, os, sub):
        from opal import models

        episub.return_value = False
        mock_args = MagicMock(name='Mock Args')
        mock_args.app = 'opal'
        mock_args.dry_run = False
        with patch.object(commandline, '_find_application_name') as namer:
            with patch.object(commandline.scaffold_utils, 'create_display_template_for') as c:
                namer.return_value = 'opal.tests'
                commandline.scaffold(mock_args)
                c.assert_any_call(models.Diagnosis, commandline.SCAFFOLDING_BASE)

    @patch('opal.models.EpisodeSubrecord.get_display_template')
    def test_episode_subrecord_no_display_template_dry_run(self, episub, os, sub):
        from opal import models

        episub.return_value = False
        mock_args = MagicMock(name='Mock Args')
        mock_args.app = 'opal'
        mock_args.dry_run = True
        with patch.object(commandline, '_find_application_name') as namer:
            with patch.object(commandline, 'write') as writer:
                namer.return_value = 'opal.tests'
                commandline.scaffold(mock_args)
                writer.assert_any_call("No Display template for <class 'opal.models.Diagnosis'>")

    @patch('opal.models.EpisodeSubrecord.get_form_template')
    def test_episode_subrecord_no_form_template(self, episub, os, sub):
        from opal import models

        episub.return_value = False
        mock_args = MagicMock(name='Mock Args')
        mock_args.app = 'opal'
        mock_args.dry_run = False
        with patch.object(commandline, '_find_application_name') as namer:
            with patch.object(commandline.scaffold_utils, 'create_form_template_for') as c:
                namer.return_value = 'opal.tests'
                commandline.scaffold(mock_args)
                c.assert_any_call(models.Diagnosis, commandline.SCAFFOLDING_BASE)

    @patch('opal.models.EpisodeSubrecord.get_form_template')
    def test_episode_subrecord_no_form_template_dry_run(self, episub, os, sub):
        from opal import models

        episub.return_value = False
        mock_args = MagicMock(name='Mock Args')
        mock_args.app = 'opal'
        mock_args.dry_run = True
        with patch.object(commandline, '_find_application_name') as namer:
            with patch.object(commandline, 'write') as writer:
                namer.return_value = 'opal.tests'
                commandline.scaffold(mock_args)
                writer.assert_any_call("No Form template for <class 'opal.models.Diagnosis'>")


class TestTestCase(OpalTestCase):

    def test_test(self):
        mock_args = MagicMock(name='Mock Args')
        with patch.object(commandline.test_runner, 'run_tests') as rt:
            commandline.test(mock_args)
            rt.assert_called_with(mock_args)


@patch('subprocess.check_output')
@patch('subprocess.check_call')
@patch('os.system')
class CheckoutTestCase(OpalTestCase):

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
