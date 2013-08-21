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
            'travel_reason': [],
            'micro_test_c_difficile': [],
            'micro_test_csf_pcr': [],
            'micro_test_ebv_serology': [],
            'micro_test_hepititis_b_serology': [],
            'micro_test_hiv': [],
            'micro_test_leishmaniasis_pcr': [],
            'micro_test_mcs': [],
            'micro_test_other': [],
            'micro_test_parasitaemia': [],
            'micro_test_respiratory_virus_pcr': [],
            'micro_test_serology': [],
            'micro_test_single_igg_test': [],
            'micro_test_single_test_pos_neg': [],
            'micro_test_single_test_pos_neg_equiv': [],
            'micro_test_stool_parasitology_pcr': [],
            'micro_test_stool_pcr': [],
            'micro_test_swab_pcr': [],
            'micro_test_syphilis_serology': [],
            'micro_test_viral_load': [],
        }
        self.assertEqual(expected_data, data)

