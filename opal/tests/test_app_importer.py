from mock import patch
from opal.core import app_importer
from django.test import TestCase, override_settings

class NewOpalObjectType(object):
    pass

class NewOpalObjectClass(NewOpalObjectType):
    pass


class AppImporterTestCase(TestCase):
    @override_settings(INSTALLED_APPS=("opal",))
    @patch("opal.core.app_importer.stringport")
    def test_class_import(self, stringport_mock):
        classes_1 = app_importer.get_subclass("someModule", NewOpalObjectType)
        classes_2 = app_importer.get_subclass("someModule", NewOpalObjectType)

        self.assertEqual([i for i in classes_1], [NewOpalObjectClass])
        self.assertEqual([i for i in classes_2], [NewOpalObjectClass])

        # should only be called once because we should only import once
        self.assertEqual(stringport_mock.call_count, 1)
