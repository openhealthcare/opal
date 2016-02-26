"""
Unittests for opal.middleware
"""
from opal.core.test import OpalTestCase

from opal import middleware

class AngularCSRFRenameTestCase(OpalTestCase):
    def test_process_request(self):
        mw = middleware.AngularCSRFRename()
        request = self.rf.get('/hai')
        request.META['HTTP_X_XSRF_TOKEN'] = 'foo'
        mw.process_request(request)
        self.assertEqual(request.META['HTTP_X_CSRFTOKEN'], 'foo')
        self.assertEqual(request.META.get('HTTP_X_XSRF_TOKEN', None), None)
