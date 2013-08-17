import json

from django.test import TestCase
from django.test.client import RequestFactory

from options.views import options_view

class OptionsTest(TestCase):
    fixtures = ['options_options']

    def test_options_view(self):
        request = RequestFactory().get('/options')
        response = options_view(request)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        expected_data = {
            'condition': ['Condition synonym', 'Some condition'],
            'antimicrobial': ['Another antimicrobial', 'Some antimicrobial'],
            'antimicrobial_route': [],
            'clinical_advice_reason_for_interaction': [],
            'destination': [],
            'hospital': [],
            'microbiology_organism': [],
            'travel_reason': []
        }
        self.assertEqual(expected_data, data)

