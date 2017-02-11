"""
Unittests for opal.core.commandline
"""
import sys

from mock import patch, MagicMock

from opal.core.test import OpalTestCase

from opal.core import commandline


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
