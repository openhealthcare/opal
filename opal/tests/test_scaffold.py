"""
Unittests for opal.core.scaffold
"""
from mock import patch
import ffs

from django.conf import settings

from opal.core.test import OpalTestCase
from opal.tests.models import Colour
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
