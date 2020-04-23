"""
Unittests for opal.core.celery
"""
from unittest.mock import patch, MagicMock

from opal.core.test import OpalTestCase

from opal.core import celery

class DebugTaskTestCase(OpalTestCase):
    def test_debug_task(self):
        with patch.object(celery.sys, 'stdout') as mock_stdout:
            celery.debug_task()
            mock_stdout.write.assert_called_with('Request: <Context: {}>\n')
