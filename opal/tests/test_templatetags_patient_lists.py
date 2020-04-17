"""
Unittests for opal.templatetags.patient_lists
"""
from unittest.mock import MagicMock

from opal.core.test import OpalTestCase

from opal.tests.test_patient_lists import TestTabbedPatientListGroup, TaggingTestPatientList
from opal.templatetags import patient_lists

class TabbedListGroupTestCase(OpalTestCase):

    def test_context(self):
        request = MagicMock(name='Mock Request')
        request.user = self.user
        mock_context = dict(
            list_group=TestTabbedPatientListGroup,
            patient_list=TaggingTestPatientList,
            request=request
        )
        ctx = patient_lists.tabbed_list_group(mock_context)
        self.assertEqual(TaggingTestPatientList, ctx['active_list'])
        expected_members = list(TestTabbedPatientListGroup.get_member_lists_for_user(self.user))
        self.assertEqual(expected_members, list(ctx['members']))
