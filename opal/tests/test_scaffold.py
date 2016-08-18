"""
Unittests for opal.core.scaffold
"""
from mock import patch, MagicMock, Mock
import ffs

from django.conf import settings

from opal.core.test import OpalTestCase
from opal.tests.models import Colour
from opal.core import scaffold
from opal.core.scaffold import (
    create_form_template_for,
    create_display_template_for
)
from opal.core import scaffold

class WriteTestCase(OpalTestCase):

    def test_write(self):
        with patch.object(scaffold, 'sys') as mocksys:
            mocksys.argv = ['not', 'te$targs']
            scaffold.write('this')
            mocksys.stdout.write.assert_called_with('this\n')

@patch('subprocess.check_call')
@patch('os.system')
class StartprojectTestCase(OpalTestCase):

    def setUp(self):
        self.path = ffs.Path.newdir()
        self.args = MagicMock(name='args')
        self.args.name = 'testapp'

    def tearDown(self):
        ffs.rm_r(self.path)

    def test_bail_if_exists(self, os, sub):
        preexisting = self.path/'testapp'
        preexisting.mkdir()
        with patch.object(scaffold.sys, 'exit') as exiter:
            scaffold.startproject(self.args, self.path)
            exiter.assert_called_with(1)

    def test_run_django_startproject(self, os, subpr):
        scaffold.startproject(self.args, self.path)
        os.assert_any_call('django-admin.py startproject testapp')

    def test_has_lookuplists_dir(self, os, subpr):
        lookuplists = self.path/'testapp/data/lookuplists'
        scaffold.startproject(self.args, self.path)
        self.assertTrue(lookuplists.is_dir)

    def test_has_gitignore(self, os, subpr):
        scaffold.startproject(self.args, self.path)
        gitignore = self.path/'testapp/.gitignore'
        self.assertTrue(gitignore.is_file)

    def test_calls_interpolate_dir(self, os, subpr):
        with patch.object(scaffold, 'interpolate_dir') as interpolate:
            with patch.object(scaffold, 'get_random_secret_key') as rnd:
                rnd.return_value = 'foobarbaz'
                scaffold.startproject(self.args, self.path)
                interpolate.assert_any_call(self.path/'testapp', name='testapp',
                                            secret_key='foobarbaz')

    def test_settings_is_our_settings(self, os, subpr):
        scaffold.startproject(self.args, self.path)
        settings = self.path/'testapp/testapp/settings.py'
        self.assertTrue('opal' in settings.contents)

    def test_sets_random_secret_key(self, os, subpr):
        with patch.object(scaffold, 'get_random_secret_key') as rnd:
            rnd.return_value = 'MyRandomKey'
            scaffold.startproject(self.args, self.path)
            settings = self.path/'testapp/testapp/settings.py'
            self.assertTrue("SECRET_KEY = 'MyRandomKey'" in settings.contents)
            rnd.assert_called_with()

    def test_has_js_dir(self, os, subpr):
        scaffold.startproject(self.args, self.path)
        js_dir = self.path/'testapp/testapp/static/js'
        self.assertTrue(js_dir.is_dir)

    def test_has_css_dir(self, os, subpr):
        scaffold.startproject(self.args, self.path)
        css_dir = self.path/'testapp/testapp/static/css'
        self.assertTrue(css_dir.is_dir)

    def test_has_js_routes(self, os, subpr):
        scaffold.startproject(self.args, self.path)
        routes = self.path/'testapp/testapp/static/js/testapp/routes.js'
        self.assertTrue(routes.is_file)

    def test_js_has_flow(self, os, subpr):
        scaffold.startproject(self.args, self.path)
        flow = self.path/'testapp/testapp/static/js/testapp/flow.js'
        self.assertTrue(flow.is_file)

    def test_has_named_templates_dir(self, os, subpr):
        scaffold.startproject(self.args, self.path)
        templates = self.path/'testapp/testapp/templates/testapp'
        self.assertTrue(templates.is_dir)

    def test_has_assets_dir(self, os, subpr):
        scaffold.startproject(self.args, self.path)
        assets = self.path/'testapp/testapp/assets'
        self.assertTrue(assets.is_dir)

    def test_has_assets_readme(self, os, subpr):
        scaffold.startproject(self.args, self.path)
        readme = self.path/'testapp/testapp/assets/README.md'
        self.assertTrue(readme.is_file)

    def test_runs_makemigrations(self, os, subpr):
        scaffold.startproject(self.args, self.path)
        subpr.assert_any_call(['python', 'testapp/manage.py',
                                  'makemigrations', 'testapp', '--traceback'])

    def test_runs_migrate(self, os, subpr):
        scaffold.startproject(self.args, self.path)
        subpr.assert_any_call(['python', 'testapp/manage.py',
                               'migrate', '--traceback'])

    def test_sets_settings(self, os, subpr):
        with patch.object(scaffold, '_set_settings_module') as settings:
            scaffold.startproject(self.args, self.path)
            settings.assert_called_with('testapp')

    def test_initialize_git(self, os, subpr):
        scaffold.startproject(self.args, self.path)
        os.assert_any_call('cd testapp; git init')


@patch("ffs.Path.__lshift__")
class FormRenderTestCase(OpalTestCase):
    def test_form_render(self, lshift):
        """ test a generic string render
        """
        scaffold_path = ffs.Path(settings.PROJECT_PATH)/'scaffolding'
        create_form_template_for(Colour, scaffold_path)
        lshift.assert_called_once_with(
            '{% load forms %}\n{% input  field="Colour.name"  %}'
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
            '{% load forms %}\n{% datepicker  field="Colour.name"  %}'
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
            '{% load forms %}\n{% datetimepicker  field="Colour.name"  %}'
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
            '{% load forms %}\n{% textarea  field="Colour.name"  %}'
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
            '{% load forms %}\n{% checkbox  field="Colour.name"  %}'
        )


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
            '<span ng-show="item.name">\n    [[ item.name | shortDateTime ]]\n   <br />\n</span>'
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
            '<span ng-show="item.name">\n    [[ item.name | shortDate ]]\n   <br />\n</span>'
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
