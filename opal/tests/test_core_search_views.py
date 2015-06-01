"""
unittests for opal.core.search.views
"""
from mock import patch

from opal.core.test import OpalTestCase

from opal.core.search import views

class PatientSearchTestCase(OpalTestCase):
    def test_query_type_defaults(self):
        request = self.rf.get('/search/patient/?name=jones')
        request.user = self.user
        with patch.object(views.queries, 'SearchBackend') as mock_search:
            mock_search.return_value.episodes_as_json.return_value = []
            resp = views.patient_search_view(request)
            criteria = [{
                'column'   : 'demographics',
                'combine'  : 'and',
                'queryType': 'Contains',
                'field'    : 'name',
                'query'    : 'jones'
            }]
            self.assertEqual(200, resp.status_code)
            mock_search.assert_called_with(request.user, criteria)

    def test_must_provide_name_or_hospital_number(self):
        request = self.rf.get('/search/patient/')
        request.user = self.user
        resp = views.patient_search_view(request)
        self.assertEqual(400, resp.status_code)
        
        
class SearchTemplateTestCase(OpalTestCase):

    def test_search_template_view(self):
        self.assertStatusCode('/search/templates/search.html/', 200)

