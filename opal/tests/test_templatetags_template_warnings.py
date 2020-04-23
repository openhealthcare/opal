from opal.core.test import OpalTestCase
from django.template import Template, Context
from unittest import mock


@mock.patch("opal.templatetags.template_warnings.warnings.warn")
class WarningsTestCase(OpalTestCase):

    def test_warning(self, warn):
        tpl = Template('{% load template_warnings %}{% warn "interesting" %}')
        tpl.render(Context({}))
        # django calls warning a lot, so lets make sure that
        # our call is used at least once
        all_args = [i[0][0] for i in warn.call_args_list]
        self.assertIn('"interesting"', all_args)

    def test_warning_error(self, warn):
        with self.assertRaises(ValueError) as err:
            tpl = Template(
                '{% load template_warnings %}{% warn "interesting" "other" %}'
            )
            tpl.render(Context({}))
        self.assertFalse(warn.called)
        self.assertEqual(
            str(err.exception), "Warnings only takes a single string message"
        )
