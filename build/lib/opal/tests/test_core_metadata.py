"""
Unittests for the opal.core.metadata module
"""
from opal import models
from opal.core.test import OpalTestCase

from opal.core import metadata

class MacroMetadataTestCase(OpalTestCase):

    def test_to_dict(self):
        macro = models.Macro(title='the title', expanded='the expanded')
        macro.save()
        expected = {
            'macros': [{'expanded': 'the expanded', 'label': 'the title'}]
        }
        self.assertEqual(expected, metadata.MacrosMetadata.to_dict())

class MicoTestDefaultsTestCase(OpalTestCase):

    def test_to_dict(self):
        expected = {
                    'igm': 'pending',
                    'igg': 'pending'
                }
        as_dict = metadata.MicroTestDefaultsMetadata.to_dict()
        self.assertEqual(expected, as_dict['micro_test_defaults']['micro_test_serology'])
