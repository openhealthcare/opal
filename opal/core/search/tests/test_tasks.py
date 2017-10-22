"""
Unittests for the opal.core.search.tasks module
"""
from mock import patch
from opal.core.test import OpalTestCase

from opal.core.search import tasks


class ExtractTestCase(OpalTestCase):

    @patch('opal.core.search.extract.zip_archive')
    def test_extract(self, zip_archive):
        zip_archive.return_value = 'Help'
        data_slice = {}
        criteria = [
            {
                u'column': u'demographics',
                u'field': u'surname',
                u'combine': u'and',
                u'query': u'Stevens',
                u'queryType': u'Equals'
            }
        ]
        extract_query = dict(
            data_slice=data_slice,
            criteria=criteria
        )
        fname = tasks.extract(self.user, extract_query)
        self.assertEqual('Help', fname)
