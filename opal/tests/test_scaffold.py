from mock import patch
import ffs

from django.conf import settings

from opal.core.test import OpalTestCase
from opal.tests.models import Colour
from opal.core.scaffold import (
    create_form_template_for,
    create_display_template_for
)


# @patch("ffs.Path.__lshift__")
# class FormRenderTestCase(OpalTestCase):
#     def test_form_render(self, lshift):
#         scaffold_path = ffs.Path(settings.PROJECT_PATH)/'scaffolding'
#         create_form_template_for(Colour, scaffold_path)
#         lshift.assert_called_once_with(
#             '{% load forms %}\n{% input  field="Colour.name"  %}'
#         )

# @patch("ffs.Path.__lshift__")
class FormRenderTestCase(OpalTestCase):
    def test_form_render(self):
        scaffold_path = ffs.Path(settings.PROJECT_PATH)/'scaffolding'
        create_form_template_for(Colour, scaffold_path)


@patch("ffs.Path.__lshift__")
class RecordRenderTestCase(OpalTestCase):
    def test_form_render(self, lshift):
        scaffold_path = ffs.Path(settings.PROJECT_PATH)/'scaffolding'
        create_display_template_for(Colour, scaffold_path)
        lshift.assert_called_once_with(
            '<span ng-show="item.name">\n    [[ item.name ]]\n   <br />\n</span>'
        )
