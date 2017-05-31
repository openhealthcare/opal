from opal.core.test import OpalTestCase
from django.template import Template, Context
import mock


@mock.patch("opal.templatetags.template_warnings.warnings.warn")
class WarningsTestCase(OpalTestCase):

    def test_warning(self, warn):
        tpl = Template('{% load template_warnings %}{% warn "interesting" %}')
        tpl.render(Context({}))
        self.assertEqual(warn.call_args_list[1][0][0], '"interesting"')

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
