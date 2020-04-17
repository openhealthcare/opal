"""
Unittests for opal.core.scaffold
"""
import os
import subprocess
import tempfile

from unittest.mock import patch, MagicMock
import ffs
import opal
from opal.tests import models

from django.conf import settings

from opal.core.test import OpalTestCase
from opal.tests.models import Colour
from opal.core import scaffold
from opal.core.scaffold import (
    create_form_template_for,
    create_display_template_for
)


@patch('subprocess.check_call')
class CallTestCase(OpalTestCase):
    def test_writes_message(self, cc):
        with patch.object(scaffold, 'write'):
            scaffold.call(('yes', 'please'))
            scaffold.write.assert_called_with('Calling: yes please')

    def test_calls_with_args(self, cc):
        scaffold.call(('yes', 'please'))
        cc.assert_called_with(('yes', 'please'))

    def test_exits_on_error(self, cc):
        with patch.object(scaffold.sys, 'exit') as exiter:
            cc.side_effect = subprocess.CalledProcessError(None, None)
            scaffold.call(('oh' 'noes'))
            exiter.assert_called_with(1)


@patch('opal.core.scaffold.call')
class CallIfExistsTestCase(OpalTestCase):
    def test_success(self, c):
        self.assertEqual(
            True,
            scaffold.call_if_exists(('hello', 'world'), 'Sorry, no greetings')
        )

    def test_file_not_found_err(self, c):
        if getattr(__builtins__, 'FileNotFoundError', None):
            c.side_effect = FileNotFoundError(2, os.strerror(2))
            with patch.object(scaffold, 'write'):
                return_value = scaffold.call_if_exists(
                    ('hello', 'world'),
                    'Sorry no greetings'
                )
                self.assertEqual(False, return_value)
                scaffold.write.assert_any_call('Sorry no greetings')

    def test_oserror(self, c):
        c.side_effect = OSError(2, os.strerror(2))
        with patch.object(scaffold, 'write'):
            return_value = scaffold.call_if_exists(
                ('hello', 'world'),
                'Sorry no greetings'
            )
            self.assertEqual(False, return_value)
            scaffold.write.assert_any_call('Sorry no greetings')

    def test_other_oserror(self, c):
        with self.assertRaises(OSError):
            c.side_effect = OSError(3, os.strerror(3))
            scaffold.call_if_exists(
                ('hello', 'world'),
                'No such process would be a weird error to get here'
            )


@patch('subprocess.check_call')
class StartpluginTestCase(OpalTestCase):
    def setUp(self):
        self.path = ffs.Path.newdir()
        self.args = 'testplugin'

    def tearDown(self):
        ffs.rm_r(self.path)

    @patch("ffs.nix.cp_r", side_effect=ffs.nix.cp_r)
    def test_tree_copied(self, cp_r, subpr):
        scaffold.start_plugin(self.args, self.path)
        self.assertTrue(cp_r.called)

    def test_creates_the_app_directory(self, subpr):
        test_plugin = self.path/'opal-testplugin/testplugin'
        scaffold.start_plugin(self.args, self.path)
        self.assertTrue(test_plugin.is_dir)

    def test_creates_appropriate_directory_with_opal_prefix(self, subpr):
        test_plugin = self.path/'opal-testplugin/testplugin'
        scaffold.start_plugin("opal-testplugin", self.path)
        self.assertTrue(test_plugin.is_dir)

    def test_creates_template_directory(self, subpr):
        template_dir = self.path/'opal-testplugin/testplugin/templates'
        scaffold.start_plugin(self.args, self.path)
        self.assertTrue(template_dir.is_dir)

    def test_creates_static_directory(self, subpr):
        static_dir = self.path/'opal-testplugin/testplugin/static'
        scaffold.start_plugin(self.args, self.path)
        self.assertTrue(static_dir.is_dir)

    def test_calls_interpolate_dir(self, subpr):
        with patch.object(scaffold, 'interpolate_dir') as interpolate:
            scaffold.start_plugin(self.args, self.path)
            self.assertEqual(interpolate.call_args[1]["name"], "testplugin")
            self.assertIn("version", interpolate.call_args[1])

    def test_creates_css_directory(self, subpr):
        css_dir = self.path/'opal-testplugin/testplugin/static/css'
        scaffold.start_plugin(self.args, self.path)
        self.assertTrue(css_dir.is_dir)

    def test_creates_controllers_directory(self, subpr):
        rpath = 'opal-testplugin/testplugin/static/js/testplugin/controllers'
        controllers_dir = self.path/rpath
        scaffold.start_plugin(self.args, self.path)
        self.assertTrue(controllers_dir.is_dir)

    def test_creates_services_directory(self, subpr):
        rpath = 'opal-testplugin/testplugin/static/js/testplugin/services'
        services_dir = self.path/rpath
        scaffold.start_plugin(self.args, self.path)
        self.assertTrue(services_dir.is_dir)

    def test_has_lookuplists_dir(self, subpr):
        rpath = 'opal-testplugin/testplugin/data/lookuplists/'
        lookuplists = self.path/rpath
        scaffold.start_plugin(self.args, self.path)
        self.assertTrue(bool(lookuplists))

    def test_creates_manifest(self, subpr):
        rpath = 'opal-testplugin/MANIFEST.in'
        manifest = self.path/rpath
        scaffold.start_plugin(self.args, self.path)
        self.assertTrue(bool(manifest))
        with open(manifest) as m:
            contents = m.read()
            self.assertIn("recursive-include testplugin/static *", contents)
            self.assertIn("recursive-include testplugin/templates *", contents)

    def test_initialize_git(self, subpr):
        scaffold.start_plugin(self.args, self.path)
        subpr.assert_any_call(('git', 'init'),
                              cwd=self.path/'opal-testplugin',
                              stdout=subprocess.PIPE)

    def test_creates_requirements(self, subpr):
        rpath = 'opal-testplugin/requirements.txt'
        requirements = self.path/rpath
        scaffold.start_plugin(self.args, self.path)
        self.assertTrue(bool(requirements))
        with open(requirements) as r:
            contents = r.read()
            self.assertIn('opal=={}'.format(opal.__version__), contents)


@patch('subprocess.check_call')
@patch.object(scaffold.management, 'call_command')
class StartprojectTestCase(OpalTestCase):

    def setUp(self):
        self.path = ffs.Path.newdir()
        self.args = 'testapp'

    def tearDown(self):
        ffs.rm_r(self.path)

    def test_bail_if_exists(self, call_command, sub):
        preexisting = self.path/'testapp'
        preexisting.mkdir()
        with patch.object(scaffold.sys, 'exit') as exiter:
            scaffold.start_project(self.args, self.path)
            exiter.assert_called_with(1)

    def test_run_django_start_project(self, call_command, subpr):
        scaffold.start_project(self.args, self.path)
        call_command.assert_any_call('startproject', 'testapp',
                                     self.path/'testapp')

    def test_has_lookuplists_dir(self, call_command, subpr):
        scaffold.start_project(self.args, self.path)
        lookuplists = self.path/'testapp/testapp/data/lookuplists/'
        self.assertTrue(bool(lookuplists))

    def test_has_gitignore(self, call_command, subpr):
        scaffold.start_project(self.args, self.path)
        gitignore = self.path/'testapp/.gitignore'
        self.assertTrue(gitignore.is_file)

    def test_calls_interpolate_dir(self, call_command, subpr):
        with patch.object(scaffold, 'interpolate_dir') as interpolate:
            with patch.object(scaffold, 'get_random_secret_key') as rnd:
                rnd.return_value = 'foobarbaz'
                scaffold.start_project(self.args, self.path)
                interpolate.assert_any_call(self.path/'testapp', name='testapp',
                                            secret_key='foobarbaz',
                                            version=opal.__version__)

    def test_settings_is_our_settings(self, call_command, subpr):
        scaffold.start_project(self.args, self.path)
        settings = self.path/'testapp/testapp/settings.py'
        self.assertTrue('opal' in settings.contents)

    def test_sets_random_secret_key(self, call_command, subpr):
        with patch.object(scaffold, 'get_random_secret_key') as rnd:
            rnd.return_value = 'MyRandomKey'
            scaffold.start_project(self.args, self.path)
            settings = self.path/'testapp/testapp/settings.py'
            self.assertTrue("SECRET_KEY = 'MyRandomKey'" in settings.contents)
            rnd.assert_called_with()

    def test_has_js_dir(self, call_command, subpr):
        scaffold.start_project(self.args, self.path)
        js_dir = self.path/'testapp/testapp/static/js'
        self.assertTrue(js_dir.is_dir)

    def test_has_css_dir(self, call_command, subpr):
        scaffold.start_project(self.args, self.path)
        css_dir = self.path/'testapp/testapp/static/css'
        self.assertTrue(css_dir.is_dir)

    def test_has_js_routes(self, call_command, subpr):
        scaffold.start_project(self.args, self.path)
        routes = self.path/'testapp/testapp/static/js/testapp/routes.js'
        self.assertTrue(routes.is_file)

    def test_has_named_templates_dir(self, call_command, subpr):
        scaffold.start_project(self.args, self.path)
        templates = self.path/'testapp/testapp/templates/testapp'
        self.assertTrue(templates.is_dir)

    def test_has_assets_dir(self, call_command, subpr):
        scaffold.start_project(self.args, self.path)
        assets = self.path/'testapp/testapp/assets'
        self.assertTrue(assets.is_dir)

    def test_has_assets_readme(self, call_command, subpr):
        scaffold.start_project(self.args, self.path)
        readme = self.path/'testapp/testapp/assets/README.md'
        self.assertTrue(readme.is_file)

    def test_creates_manifest(self, call_command, subpr):
        scaffold.start_project(self.args, self.path)
        manifest = self.path/'testapp/MANIFEST.in'
        self.assertTrue(bool(manifest))
        with open(manifest) as m:
            contents = m.read()
            self.assertIn("recursive-include testapp/static *", contents)
            self.assertIn("recursive-include testapp/templates *", contents)
            self.assertIn("recursive-include testapp/assets *", contents)

    def test_runs_makemigrations(self, call_command, subpr):
        scaffold.start_project(self.args, self.path)
        subpr.assert_any_call(['python', os.path.join('testapp', 'manage.py'),
                                  'makemigrations', 'testapp', '--traceback'])

    @patch.object(scaffold.sys, 'exit')
    def test_if_subprocess_errors(self, exiter, call_command, subpr):
        subpr.side_effect = subprocess.CalledProcessError(None, None)
        scaffold.start_project(self.args, self.path)
        subpr.assert_any_call(['python', os.path.join('testapp', 'manage.py'),
                                  'makemigrations', 'testapp', '--traceback'])
        exiter.assert_any_call(1)

    def test_runs_migrate(self, call_command, subpr):
        scaffold.start_project(self.args, self.path)
        subpr.assert_any_call(['python', os.path.join('testapp', 'manage.py'),
                               'migrate', '--traceback'])

    def test_runs_createopalsuperuser(self, call_command, subpr):
        scaffold.start_project(self.args, self.path)
        subpr.assert_any_call(['python', os.path.join('testapp', 'manage.py'),
                               'createopalsuperuser', '--traceback'])

    def test_initialize_git(self, call_command, subpr):
        scaffold.start_project(self.args, self.path)
        subpr.assert_any_call(('git', 'init'),
                              cwd=self.path/'testapp',
                              stdout=subprocess.PIPE)

    def test_creates_requirements(self, call_command, subpr):
        scaffold.start_project(self.args, self.path)
        requirements = self.path/'testapp/requirements.txt'
        self.assertTrue(bool(requirements))
        with open(requirements) as r:
            contents = r.read()
            self.assertIn('opal=={}'.format(opal.__version__), contents)


@patch("ffs.Path.__lshift__")
class RecordRenderTestCase(OpalTestCase):
    def test_form_render(self, lshift):
        """ test a generic string render
        """
        scaffold_path = ffs.Path(settings.PROJECT_PATH)/'scaffolding'
        create_display_template_for(Colour, scaffold_path)
        lshift.assert_called_once_with(
            '<span ng-show="item.name">\n    [[ item.name ]]\n   <br />\n</span>'
        )

    @patch.object(Colour, "build_field_schema")
    def test_datetime_render(self, build_field_schema, lshift):
        build_field_schema.return_value = {
            'lookup_list': None,
            'model': 'Colour',
            'name': 'name',
            'title': 'Name',
            'type': 'date_time'
        },
        scaffold_path = ffs.Path(settings.PROJECT_PATH)/'scaffolding'
        create_display_template_for(Colour, scaffold_path)
        lshift.assert_called_once_with(
            '<span ng-show="item.name">\n    [[ item.name | displayDateTime ]]\n   <br />\n</span>'
        )

    @patch.object(Colour, "build_field_schema")
    def test_date_render(self, build_field_schema, lshift):
        build_field_schema.return_value = {
            'lookup_list': None,
            'model': 'Colour',
            'name': 'name',
            'title': 'Name',
            'type': 'date'
        },
        scaffold_path = ffs.Path(settings.PROJECT_PATH)/'scaffolding'
        create_display_template_for(Colour, scaffold_path)
        lshift.assert_called_once_with(
            '<span ng-show="item.name">\n    [[ item.name | displayDate ]]\n   <br />\n</span>'
        )

    @patch.object(Colour, "build_field_schema")
    def test_time_render(self, build_field_schema, lshift):
        build_field_schema.return_value = {
            'lookup_list': None,
            'model': 'Colour',
            'name': 'name',
            'title': 'Name',
            'type': 'time'
        },
        scaffold_path = ffs.Path(settings.PROJECT_PATH)/'scaffolding'
        create_display_template_for(Colour, scaffold_path)
        lshift.assert_called_once_with(
            '<span ng-show="item.name">\n    [[ item.name | shortTime ]]\n   <br />\n</span>'
        )

    @patch.object(Colour, "build_field_schema")
    def test_boolean_render(self, build_field_schema, lshift):
        build_field_schema.return_value = {
            'lookup_list': None,
            'model': 'Colour',
            'name': 'name',
            'title': 'Name',
            'type': 'boolean'
        },
        scaffold_path = ffs.Path(settings.PROJECT_PATH)/'scaffolding'
        create_display_template_for(Colour, scaffold_path)
        lshift.assert_called_once_with(
            '<span ng-show="item.name">\n     Name\n   <br />\n</span>'
        )

    @patch.object(Colour, "build_field_schema")
    def test_null_boolean_render(self, build_field_schema, lshift):
        build_field_schema.return_value = {
            'lookup_list': None,
            'model': 'Colour',
            'name': 'name',
            'title': 'Name',
            'type': 'null_boolean'
        },
        scaffold_path = ffs.Path(settings.PROJECT_PATH)/'scaffolding'
        create_display_template_for(Colour, scaffold_path)
        lshift.assert_called_once_with(
            '<span ng-show="item.name">\n     Name\n   <br />\n</span>'
        )

    @patch('ffs.Path.__bool__')
    @patch('ffs.Path.__nonzero__')
    @patch('ffs.Path.mkdir')
    @patch.object(Colour, "build_field_schema")
    def test_makes_records_dir_if_does_not_exist(self, build_field_schema, mkdir, nonzero,
                                                 booler, lshift):
        build_field_schema.return_value = {
            'lookup_list': None,
            'model': 'Colour',
            'name': 'name',
            'title': 'Name',
            'type': 'null_boolean'
        },

        # We need both of these to make sure this works on both Python3 and Python2
        nonzero.return_value = False
        booler.return_value = False

        scaffold_path = ffs.Path(settings.PROJECT_PATH)/'scaffolding'
        create_display_template_for(Colour, scaffold_path)
        mkdir.assert_called_once_with()


class GetTemplateDirFromRecordTestCase(OpalTestCase):

    def test_get_template_dir_from_record_with_pyc(self):
        with patch.object(scaffold.inspect, 'getfile') as getter:
            getter.return_value = os.path.join('me', 'models.pyc')
            d = scaffold._get_template_dir_from_record(MagicMock())
            self.assertEqual(os.path.join('me', 'templates'), str(d))

    def test_get_template_dir_from_package_models(self):
        with patch.object(scaffold.inspect, 'getfile') as getter:
            getter.return_value = os.path.join('me', 'models', 'clinic.py')
            d = scaffold._get_template_dir_from_record(MagicMock())
            self.assertEqual(os.path.join('me', 'templates'), str(d))

    def test_template_dir_not_found(self):
        with patch.object(scaffold.sys, 'exit') as exiter:
            with patch.object(scaffold.inspect, 'getfile') as getter:
                getter.return_value = os.path.join('me', 'you', 'clinic.py')
                d = scaffold._get_template_dir_from_record(MagicMock())
                exiter.asser_called_with(1)



@patch('opal.core.scaffold.write')
@patch('opal.core.scaffold.apps')
@patch('opal.core.scaffold.create_display_template_for')
@patch('opal.core.scaffold.create_form_template_for')
@patch('opal.core.scaffold.management.call_command')
class ScaffoldTestCase(OpalTestCase):
    def test_scaffold(
        self,
        call_command,
        form_template,
        display_template,
        apps,
        write
    ):
        apps.all_models = {"opal": {'dinner': models.Dinner}}
        scaffold.scaffold_subrecords('opal')
        self.assertEqual(call_command.call_count, 2)
        call_args = call_command.call_args_list
        self.assertEqual(
            call_args[0][0],
            (
                "makemigrations",
                "opal",
                "--traceback"
            )
        )

        self.assertEqual(
            call_args[1][0],
            (
                "migrate",
                "opal",
                "--traceback"
            )
        )
        self.assertEqual(
            form_template.call_count,
            1
        )
        self.assertEqual(
            form_template.call_args[0][0],
            models.Dinner
        )

        self.assertEqual(
            display_template.call_count,
            1
        )
        self.assertEqual(
            display_template.call_args[0][0],
            models.Dinner
        )
        self.assertFalse(write.called)

    def test_scaffold_raises_an_error(
        self,
        call_command,
        form_template,
        display_template,
        apps,
        write
    ):
        apps.all_models = []
        with self.assertRaises(ValueError) as e:
            scaffold.scaffold_subrecords('unreal')

        self.assertEqual(
            "Unable to find app unreal in settings.INSTALLED_APPS",
            str(e.exception)
        )



    def test_dry_run(
        self,
        call_command,
        form_template,
        display_template,
        apps,
        write
    ):
        apps.all_models = {"opal": {'dinner': models.Dinner}}
        scaffold.scaffold_subrecords('opal', dry_run=True)
        self.assertEqual(call_command.call_count, 1)
        call_args = call_command.call_args_list
        self.assertEqual(
            call_args[0][0],
            (
                "makemigrations",
                "opal",
                "--traceback",
                "--dry-run"
            )
        )

        self.assertEqual(write.call_count, 2)
        call_args = write.call_args_list
        self.assertEqual(
            call_args[0][0],
            ("No Display template for {}".format(models.Dinner),)
        )

        self.assertEqual(
            call_args[1][0],
            ("No Form template for {}".format(models.Dinner),)
        )

    def test_no_migrations(
        self,
        call_command,
        form_template,
        display_template,
        apps,
        write
    ):
        apps.all_models = {"opal": {'dinner': models.Dinner}}
        scaffold.scaffold_subrecords('opal', migrations=False)
        self.assertFalse(call_command.called)

        self.assertEqual(
            form_template.call_count,
            1
        )
        self.assertEqual(
            form_template.call_args[0][0],
            models.Dinner
        )

        self.assertEqual(
            display_template.call_count,
            1
        )
        self.assertEqual(
            display_template.call_args[0][0],
            models.Dinner
        )
        self.assertFalse(write.called)

    def test_episode_subrecord_display_template(
        self,
        call_command,
        form_template,
        display_template,
        apps,
        write
    ):
        apps.all_models = {"opal": {'dinner': models.Dinner}}
        with patch.object(
            models.Dinner, "get_display_template"
        ) as get_display_template:
            get_display_template.return_value = True
            scaffold.scaffold_subrecords('opal')
        self.assertFalse(display_template.called)

    def test_episode_subrecord_form_template(
        self,
        call_command,
        form_template,
        display_template,
        apps,
        write
    ):
        apps.all_models = {"opal": {'dinner': models.Dinner}}
        with patch.object(
            models.Dinner, "get_form_template"
        ) as get_display_template:
            get_display_template.return_value = True
            scaffold.scaffold_subrecords('opal')
        self.assertFalse(form_template.called)


class ScaffoldIntegrationTestCase(OpalTestCase):
    @patch('opal.core.scaffold._get_template_dir_from_record')
    def test_integration(self, get_template_dir):
        """
            A quick cover all test that, um doesn't cover everything
            apart from django migrations/makemigrations
            can we confirm with a superficial test
            that no other apis internal or external
            that we are using have changed.
        """
        tmp_dir = tempfile.mkdtemp()
        get_template_dir.return_value = ffs.Path(tmp_dir)
        scaffold.scaffold_subrecords('tests', migrations=False)
        self.assertTrue(
            os.path.isfile(
                os.path.join(tmp_dir, "records", "hat_wearer.html")
            )
        )
        self.assertTrue(
            os.path.isfile(
                os.path.join(tmp_dir, "forms", "hat_wearer_form.html")
            )
        )


@patch("ffs.Path.__lshift__")
class FormRenderTestCase(OpalTestCase):
    def test_form_render(self, lshift):
        """ test a generic string render
        """
        scaffold_path = ffs.Path(settings.PROJECT_PATH)/'scaffolding'
        create_form_template_for(Colour, scaffold_path)
        lshift.assert_called_once_with(
            '{% load forms %}\n{% input field="Colour.name" %}'
        )

    @patch.object(Colour, "build_field_schema")
    def test_date_render(self, build_field_schema, lshift):
        build_field_schema.return_value = {
            'lookup_list': None,
            'model': 'Colour',
            'name': 'name',
            'title': 'Name',
            'type': 'date'
        },
        scaffold_path = ffs.Path(settings.PROJECT_PATH)/'scaffolding'
        create_form_template_for(Colour, scaffold_path)
        lshift.assert_called_once_with(
            '{% load forms %}\n{% datepicker field="Colour.name" %}'
        )

    @patch.object(Colour, "build_field_schema")
    def test_datetime_render(self, build_field_schema, lshift):
        build_field_schema.return_value = {
            'lookup_list': None,
            'model': 'Colour',
            'name': 'name',
            'title': 'Name',
            'type': 'date_time'
        },
        scaffold_path = ffs.Path(settings.PROJECT_PATH)/'scaffolding'
        create_form_template_for(Colour, scaffold_path)
        lshift.assert_called_once_with(
            '{% load forms %}\n{% datetimepicker field="Colour.name" %}'
        )

    @patch.object(Colour, "build_field_schema")
    def test_datetime_render(self, build_field_schema, lshift):
        build_field_schema.return_value = {
            'lookup_list': None,
            'model': 'Colour',
            'name': 'name',
            'title': 'Name',
            'type': 'time'
        },
        scaffold_path = ffs.Path(settings.PROJECT_PATH)/'scaffolding'
        create_form_template_for(Colour, scaffold_path)
        lshift.assert_called_once_with(
            '{% load forms %}\n{% timepicker field="Colour.name" %}'
        )

    @patch.object(Colour, "build_field_schema")
    def test_text_render(self, build_field_schema, lshift):
        build_field_schema.return_value = {
            'lookup_list': None,
            'model': 'Colour',
            'name': 'name',
            'title': 'Name',
            'type': 'text'
        },
        scaffold_path = ffs.Path(settings.PROJECT_PATH)/'scaffolding'
        create_form_template_for(Colour, scaffold_path)
        lshift.assert_called_once_with(
            '{% load forms %}\n{% textarea field="Colour.name" %}'
        )

    @patch.object(Colour, "build_field_schema")
    def test_boolean_render(self, build_field_schema, lshift):
        build_field_schema.return_value = {
            'lookup_list': None,
            'model': 'Colour',
            'name': 'name',
            'title': 'Name',
            'type': 'boolean'
        },
        scaffold_path = ffs.Path(settings.PROJECT_PATH)/'scaffolding'
        create_form_template_for(Colour, scaffold_path)
        lshift.assert_called_once_with(
            '{% load forms %}\n{% checkbox field="Colour.name" %}'
        )

    @patch.object(Colour, "build_field_schema")
    def test_integer_render(self, build_field_schema, lshift):
        build_field_schema.return_value = {
            'lookup_list': None,
            'model': 'Colour',
            'name': 'number',
            'title': 'Number',
            'type': 'integer'
        },
        scaffold_path = ffs.Path(settings.PROJECT_PATH)/'scaffolding'
        create_form_template_for(Colour, scaffold_path)
        lshift.assert_called_once_with(
            '{% load forms %}\n{% input field="Colour.number" %}'
        )

    @patch.object(Colour, "build_field_schema")
    def test_float_render(self, build_field_schema, lshift):
        build_field_schema.return_value = {
            'lookup_list': None,
            'model': 'Colour',
            'name': 'number',
            'title': 'Number',
            'type': 'float'
        },
        scaffold_path = ffs.Path(settings.PROJECT_PATH)/'scaffolding'
        create_form_template_for(Colour, scaffold_path)
        lshift.assert_called_once_with(
            '{% load forms %}\n{% input field="Colour.number" %}'
        )

    @patch('ffs.Path.__bool__')
    @patch('ffs.Path.__nonzero__')
    @patch('ffs.Path.mkdir')
    @patch.object(Colour, "build_field_schema")
    def test_makes_forms_dir_if_does_not_exist(self, build_field_schema, mkdir, nonzero,
                                               booler, lshift):
        build_field_schema.return_value = {
            'lookup_list': None,
            'model': 'Colour',
            'name': 'name',
            'title': 'Name',
            'type': 'null_boolean'
        },

        # We need both of these to make sure this works on both Python3 and Python2
        nonzero.return_value = False
        booler.return_value = False

        scaffold_path = ffs.Path(settings.PROJECT_PATH)/'scaffolding'
        create_form_template_for(Colour, scaffold_path)
        mkdir.assert_called_once_with()
