"""
Allowing us to define application medatada that we can
serve to client applications via a JSON API.

We also define some metadata defaults that we don't currently have
better places for.

These should eventually be moved out.
"""
from opal.core import discoverable


class Metadata(discoverable.DiscoverableFeature):
    module_name = 'metadata'


class MacrosMetadata(Metadata):
    slug = 'macros'

    @classmethod
    def to_dict(klass, **kw):
        from opal.models import Macro

        return {
            klass.slug: Macro.to_dict()
        }


class MicroTestDefaultsMetadata(Metadata):
    slug = 'micro_test_defaults'

    @classmethod
    def to_dict(klass, **kw):
        return {
            klass.slug: {
                'micro_test_serology': {
                    'igm': 'pending',
                    'igg': 'pending'
                },
                'micro_test_ebv_serology': {
                    'vca_igm' : 'pending',
                    'vca_igg' : 'pending',
                    'ebna_igg': 'pending'
                },
                'micro_test_hiv': {
                    'result': 'pending'
                },
                'micro_test_hepititis_b_serology': {
                    'hbsag'          : 'pending',
                    'anti_hbs'       : 'pending',
                    'anti_hbcore_igm': 'pending',
                    'anti_hbcore_igg': 'pending'
                },
                'micro_test_syphilis_serology': {
                    'tppa': 'pending'
                },
                'micro_test_single_test_pos_neg': {
                    'result': 'pending'
                },
                'micro_test_single_test_pos_neg_equiv': {
                    'result': 'pending'
                },
                'micro_test_single_igg_test': {
                    'result': 'pending'
                },
                'micro_test_swab_pcr': {
                    'hsv': 'pending',
                    'vzv': 'pending',
                    'syphilis': 'pending'
                },
                'micro_test_c_difficile': {
                    'c_difficile_antigen': 'pending',
                    'c_difficile_toxin': 'pending'
                },
                'micro_test_leishmaniasis_pcr': {
                    'result': 'pending'
                },
                'micro_test_csf_pcr': {
                    'hsv_1': 'pending',
                    'hsv_2': 'pending',
                    'enterovirus': 'pending',
                    'cmv': 'pending',
                    'ebv': 'pending',
                    'vzv': 'pending'
                },
                'micro_test_respiratory_virus_pcr': {
                    'influenza_a': 'pending',
                    'influenza_b': 'pending',
                    'parainfluenza': 'pending',
                    'metapneumovirus': 'pending',
                    'rsv': 'pending',
                    'adenovirus': 'pending',
                },
                'micro_test_stool_pcr': {
                    'norovirus': 'pending',
                    'rotavirus': 'pending',
                    'adenovirus': 'pending',
                },
                'micro_test_stool_parasitology_pcr': {
                    'giardia': 'pending',
                    'entamoeba_histolytica': 'pending',
                    'cryptosporidium': 'pending'
                }
            }
        }
