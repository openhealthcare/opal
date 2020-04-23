"""
unittests for the opal.core.pathways.templatetags package
"""
from django.template import Template, Context
from unittest.mock import patch

from opal.core.test import OpalTestCase
from opal.tests.models import Colour

from opal.core.pathway.templatetags import pathways as template_tags


@patch.object(Colour, 'get_form_template')
class MultSaveTest(OpalTestCase):

    def test_defaults(self, get_form_template):
        template = Template('{% load pathways %}{% multisave models.Colour %}')
        models = dict(models=dict(Colour=Colour))
        rendered = template.render(Context(models))
        self.assertIn('save-multiple-wrapper="editing.colour"', rendered)

    def test_global_template_context_not_changed(self, get_form_template):
        template = Template("""
            {% load pathways %}{% multisave models.Colour %}{{ model }}
        """)
        models = dict(models=dict(Colour=Colour))
        rendered = template.render(Context(models))
        self.assertFalse(rendered.strip().endswith("editing.colour"))

    def test_nested_template_context(self, get_form_template):
        template = Template(
            '{% load pathways %}{% multisave models.Colour %}OMG: {{ some_test_var }}'
        )
        models = dict(models=dict(Colour=Colour), some_test_var="onions")
        resp = template.render(Context(models))
        self.assertIn('OMG: onions', resp)

    def test_add_common_context(self, get_form_template):
        ctx = template_tags.add_common_context({}, Colour)
        self.assertEqual(ctx["subrecord"], Colour)
        self.assertEqual(ctx["model"], "editing.colour")

    def test_multisave(self, get_form_template):
        ctx = template_tags.multisave({}, Colour)
        self.assertEqual(ctx["subrecord"], Colour)
        self.assertEqual(ctx["model"], "editing.colour")
