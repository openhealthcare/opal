"""
Unittests for the opal.core.discoverable module
"""
from mock import patch
from django.test import override_settings
from opal.core.test import OpalTestCase

from opal.core import discoverable

class NewOpalObjectType(object):
    pass

class NewOpalObjectClass(NewOpalObjectType):
    pass

class MyPassingFeature(discoverable.DiscoverableFeature):
    pass

class WatFeature(discoverable.DiscoverableFeature):
    name = 'wat'
    module_name = 'wat'

class ColourFeature(discoverable.DiscoverableFeature):
    module_name = 'colours'

class BlueColour(ColourFeature):
    name = 'Blue'

class RedColour(ColourFeature):
    name = 'Red'

class SeaGreenColour(ColourFeature):
    name = 'Sea Green'



class AppImporterTestCase(OpalTestCase):

    @override_settings(INSTALLED_APPS=("opal",))
    @patch("opal.core.discoverable.stringport")
    def test_class_import(self, stringport_mock):
        classes_1 = discoverable.get_subclass("someModule", NewOpalObjectType)
        classes_2 = discoverable.get_subclass("someModule", NewOpalObjectType)

        self.assertEqual([i for i in classes_1], [NewOpalObjectClass])
        self.assertEqual([i for i in classes_2], [NewOpalObjectClass])

        # should only be called once because we should only import once
        self.assertEqual(stringport_mock.call_count, 1)


class DiscoverableFeatureTestCase(OpalTestCase):

    def test_slug_for_no_implementation(self):
        with self.assertRaises(ValueError):
            MyPassingFeature.slug()

    def test_slug_for_implementation(self):
        self.assertEqual('wat', WatFeature.slug())

    def test_slug_for_subclass(self):
        self.assertEqual('red', RedColour.slug())

    def test_slug_for_multi_word_name(self):
        self.assertEqual('sea_green', SeaGreenColour.slug())

    def test_list_for_no_implementation(self):
        with self.assertRaises(ValueError):
            MyPassingFeature.list()

    def test_list_no_subclasses(self):
        self.assertEqual([], list(WatFeature.list()))

    def test_list_subclasses(self):
        subs = list(ColourFeature.list())
        self.assertEqual(3, len(subs))
        for s in [BlueColour, RedColour, SeaGreenColour]:
            self.assertIn(s, subs)

    def test_get_not_a_thing(self):
        with self.assertRaises(ValueError):
            ColourFeature.get('border_collie')

    def test_get_exists(self):
        self.assertEqual(RedColour, ColourFeature.get('red'))
