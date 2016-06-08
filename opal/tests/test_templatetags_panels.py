"""
Tests create_singletons command
"""
from django.template import Template, Context
from opal.core.test import OpalTestCase
from opal.templatetags import panels
from opal.tests.models import Demographics
from opal.tests.models import HatWearer


class RecordPanelTestCase(OpalTestCase):
    def test_record_panel(self):
        expected = dict(
            name='demographics',
            singleton=True,
            title='Demographics',
            detail_template='records/demographics_detail.html',
            icon=None,
            editable=1,
            angular_filter=None,
            noentries=None,
            only_display_if_exists=False,
            full_width=False,
            is_patient_subrecord=True,
        )
        result = panels.record_panel(Demographics())
        self.assertEqual(expected, result)

    def test_model_pass_through(self):
        result = panels.record_panel(HatWearer)
        self.assertEqual(result["title"], "HatWearer")
        self.assertEqual(
            result["detail_template"], HatWearer.get_detail_template()
        )
        self.assertEqual(
            result["singleton"], False
        )

    def test_render(self):
        template = Template(
            '{% load panels %}{% record_panel models.HatWearer %}'
        )
        ctx = {"models": {"HatWearer": HatWearer}}
        result = template.render(Context(ctx))
        self.assertIn('HatWearer', result)

    def test_error_thrown(self):
        template = Template(
            '{% load panels %}{% record_panel models.ThisDoesntExist %}'
        )
        ctx = {"models": {"HatWearer": HatWearer}}
        with self.assertRaises(ValueError) as e:
            template.render(Context(ctx))

        self.assertEqual(e.exception.message, 'Unable to find a subrecord')


class RecordTimelineTestCase(OpalTestCase):
    def test_record_timeline(self):
        expected = dict(
            name='demographics',
            title='Demographics',
            detail_template='records/demographics_detail.html',
            icon=None,
            editable=True,
            whenfield='when'
        )
        result = panels.record_timeline(Demographics(), 'when')
        self.assertEqual(expected, result)


class TemasPanelTestCase(OpalTestCase):
    def test_teams_panel(self):
        self.assertEqual({}, panels.teams_panel())
