"""
Unittests for opal.models
"""
from mock import patch
from opal.core.test import OpalTestCase

from opal import models

class SubrecordTestCase(OpalTestCase):

    @patch('opal.models.select_template')
    def test_display_template(self, select):
        models.Subrecord.get_display_template()
        select.assert_called_with(['records/subrecord.html'])

    @patch('opal.models.select_template')
    def test_display_template_team(self, select):
        models.Subrecord.get_display_template(team='test')
        select.assert_called_with([
            'records/test/subrecord.html',
            'records/subrecord.html',
        ])

    @patch('opal.models.select_template')
    def test_display_template_subteam(self, select):
        models.Subrecord.get_display_template(team='test', subteam='really')
        select.assert_called_with([
            'records/test/really/subrecord.html',
            'records/test/subrecord.html',
            'records/subrecord.html'
        ])

    @patch('opal.models.select_template')
    def test_detail_template(self, select):
        models.Subrecord.get_detail_template()
        select.assert_called_with([
            'records/subrecord_detail.html',
            'records/subrecord.html'
        ])

    @patch('opal.models.select_template')
    def test_detail_template_team(self, select):
        models.Subrecord.get_detail_template(team='test')
        select.assert_called_with([
            'records/subrecord_detail.html',
            'records/subrecord.html'
        ])

    @patch('opal.models.select_template')
    def test_detail_template_subteam(self, select):
        models.Subrecord.get_detail_template(team='test', subteam='really')
        select.assert_called_with(['records/subrecord_detail.html', 'records/subrecord.html'])

    @patch('opal.models.select_template')
    def test_form_template(self, select):
        models.Subrecord.get_modal_template()
        select.assert_called_with(['modals/subrecord_modal.html'])

    @patch('opal.models.select_template')
    def test_modal_template_team(self, select):
        models.Subrecord.get_modal_template(team='test')
        select.assert_called_with([
            'modals/test/subrecord_modal.html',
            'modals/subrecord_modal.html'
        ])

    @patch('opal.models.select_template')
    def test_modal_template_subteam(self, select):
        models.Subrecord.get_modal_template(team='test', subteam='really')
        select.assert_called_with([
            'modals/test/really/subrecord_modal.html',
            'modals/test/subrecord_modal.html',
            'modals/subrecord_modal.html',
        ])
