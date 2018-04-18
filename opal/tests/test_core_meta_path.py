"""
Unittests for opal.core.meta_path
"""
from opal.core.test import OpalTestCase

from opal.tests import models
from opal.tests.models import Birthday

from opal.core import meta_path

class DynamicSubrecordModuleTestCase(OpalTestCase):

    def test_existing_subrecord(self):
        bd = meta_path.DynamicSubrecordModule(
            'opal.application_subrecords'
        ).Birthday
        self.assertEqual(Birthday, bd)

    def test_missing_subrecord(self):
        with self.assertRaises(AttributeError):
            module = meta_path.DynamicSubrecordModule(
                'opal.application_subrecords'
            )
            Mule = module.Mule


class ApplicationSubrecordImporterTestCase(OpalTestCase):

    def test_find_module_in_namespace(self):
        importer = meta_path.ApplicationSubrecordImporter()
        found = importer.find_module('opal.application_subrecords')
        self.assertEqual(found, importer)

    def test_find_module_outside_namespace(self):
        importer = meta_path.ApplicationSubrecordImporter()
        self.assertEqual(
            None,
            importer.find_module('bpython')
        )

    def test_load_module(self):
        importer = meta_path.ApplicationSubrecordImporter()
        module = importer.load_module('opal.application_subrecords')
        self.assertIsInstance(module, meta_path.DynamicSubrecordModule)


class ImportSyntaxTestCase(OpalTestCase):

    def test_import(self):
        from opal.application_subrecords import Dinner
        self.assertEqual(models.Dinner, Dinner)

    def test_import_as(self):
        from opal.application_subrecords import HouseOwner as LandedGentry
        self.assertEqual(models.HouseOwner, LandedGentry)
