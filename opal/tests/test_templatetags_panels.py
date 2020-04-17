"""
Tests create_singletons command
"""
import os

from unittest.mock import patch

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
            detail_template=os.path.join('records', 'demographics_detail.html'),
            icon='fa fa-user',
            editable=1,
            angular_filter=None,
            noentries=None,
            only_display_if_exists=False,
            full_width=False,
            is_patient_subrecord=True,
        )
        result = panels.record_panel(Context({}), Demographics())
        self.assertEqual(expected, result.dicts[-1])

    def test_model_pass_through(self):
        result = panels.record_panel(Context({}), HatWearer)
        self.assertEqual(result["title"], "Wearer of Hats")
        self.assertEqual(
            result["detail_template"], HatWearer.get_detail_template()
        )
        self.assertEqual(
            result["singleton"], False
        )

    def test_context(self):
        """ context should include logic from template
            context processors, but should not
            pollute the global context with this information.
        """
        template = Template(
            '{% load panels %}{{ title }}{% record_panel models.HatWearer %}{{ title }}'
        )
        ctx = {"models": {"HatWearer": HatWearer}, "title": "someTitle"}
        result = str(template.render(Context(ctx)))
        self.assertTrue(result.startswith('someTitle'))
        self.assertTrue(result.endswith('someTitle'))

        # the rest of the result should just use the hat wearter title
        # so lets just remove the start and end
        result = result.split("someTitle", 1)[1].rsplit("someTitle", 1)[0]
        self.assertFalse("someTitle" in result)
        self.assertIn(HatWearer.get_display_name(), result)

    def test_render(self):
        template = Template(
            '{% load panels %}{% record_panel models.HatWearer %}'
        )
        ctx = {"models": {"HatWearer": HatWearer}}
        result = template.render(Context(ctx))
        self.assertIn('Wearer of Hats', result)

    def test_error_thrown(self):
        template = Template(
            '{% load panels %}{% record_panel models.ThisDoesntExist %}'
        )
        ctx = {"models": {"HatWearer": HatWearer}}
        with self.assertRaises(ValueError):
            template.render(Context(ctx))


class RecordTimelineTestCase(OpalTestCase):

    def test_record_timeline(self):
        expected = dict(
            name='demographics',
            title='Demographics',
            detail_template=os.path.join('records', 'demographics_detail.html'),
            icon='fa fa-user',
            editable=True,
            whenfield='when'
        )
        result = panels.record_timeline(Demographics(), 'when')
        self.assertEqual(expected, result)

    def test_record_timeline_uses_get_display_name(self):
        with patch.object(Demographics, 'get_display_name') as display:
            display.return_value = 'Person Deets'
            result = panels.record_timeline(Demographics(), 'when')
            self.assertEqual('Person Deets', result['title'])


class TemasPanelTestCase(OpalTestCase):
    def test_teams_panel(self):
        self.assertEqual({}, panels.teams_panel())


class AlignedPairsTestCase(OpalTestCase):
    def test_aligned_pairs(self):
        template = Template(
            """
            {% load panels %}
            {% aligned_pair model="episode.start_date | displayDate" label="Start Date"%}
            """
        )
        result = template.render(Context({}))
        self.assertIn('[[ episode.start_date | displayDate ]]', result)
        self.assertIn('Start Date', result)
