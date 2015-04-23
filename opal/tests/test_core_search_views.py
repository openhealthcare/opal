"""
unittests for opal.core.search.views
"""
from opal.core.test import OpalTestCase

from opal.core.search import views

class SearchTemplateTestCase(OpalTestCase):

    def test_search_template_view(self):
        self.assertStatusCode('/search/templates/search.html/', 200)

