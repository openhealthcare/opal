"""
Tests for OpalTestCase helpers that might not be explicitly used in OPAL itself
but are useful for applications.
"""
from unittest.mock import patch

from opal.core.test import OpalTestCase

class OpalTestCaseTestCase(OpalTestCase):

    def test_post_json(self):
        with patch.object(self.client, 'post') as mock_post:
            self.post_json('/foo/', {'water': 'Yes please'})
            mock_post.assert_called_once_with(
                '/foo/',
                content_type='application/json',
                data='{"water": "Yes please"}'
            )

    def test_put_json(self):
        with patch.object(self.client, 'put') as mock_put:
            self.put_json('/foo/', {'water': 'Yes please'})
            mock_put.assert_called_once_with(
                '/foo/',
                content_type='application/json',
                data='{"water": "Yes please"}'
            )
