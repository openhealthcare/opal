"""
Unittests for the opal.core.search.tasks module
"""
from unittest.mock import patch
from opal.core.test import OpalTestCase

from opal.core.search import tasks


class ExtractTestCase(OpalTestCase):

    @patch('opal.core.search.extract.zip_archive')
    def test_extract(self, zip_archive):
        zip_archive.return_value = 'Help'
        criteria = [
            {
                u'column': u'demographics',
                u'field': u'surname',
                u'combine': u'and',
                u'query': u'Stevens',
                u'queryType': u'Equals'
            }
        ]
        fname = tasks.extract(self.user, criteria)
        self.assertEqual('Help', fname)
