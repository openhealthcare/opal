"""
Unittests for the opal.core.discoverable module
"""
from mock import patch
from django.test import override_settings

from opal.core import exceptions
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


class BombFeature(discoverable.DiscoverableFeature):
    module_name = 'bombs'
    blow_up = False

    @classmethod
    def is_valid(klass):
        if klass.blow_up == True:
            from opal.core.exceptions import InvalidDiscoverableFeatureError
            raise InvalidDiscoverableFeatureError('BLOWING UP')


class Threat(BombFeature): pass


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

    def test_is_valid_will_blow_up(self):

        # We only care that the above class did not raise an exception.
        self.assertTrue(True)

        with self.assertRaises(exceptions.InvalidDiscoverableFeatureError):
            class Detonate(BombFeature):
                blow_up = True

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

    def test_list_invalid_subclasses(self):
        self.assertEqual([Threat], list(BombFeature.list()))

    def test_get_not_a_thing(self):
        with self.assertRaises(ValueError):
            ColourFeature.get('border_collie')

    def test_get_exists(self):
        self.assertEqual(RedColour, ColourFeature.get('red'))


class SortedFeature(discoverable.SortableFeature,
                    discoverable.DiscoverableFeature):
    module_name = 'sorted'

class Sorted2(SortedFeature):
    order = 2

class Sorted3(SortedFeature):
    order = 3

class Sorted1(SortedFeature):
    order = 1


class SortableFeatureTestCase(OpalTestCase):

    def test_list_respects_order(self):
        expected = [Sorted1, Sorted2, Sorted3]
        self.assertEqual(expected, list(SortedFeature.list()))

    def test_sortable_without_module_name(self):
        class Nope(discoverable.SortableFeature): pass

        with self.assertRaises(ValueError):
            Nope.list()

class SometimesFeature(discoverable.DiscoverableFeature, discoverable.RestrictableFeature):
    module_name = 'sometimes'

class Available(SometimesFeature): pass

class Unavailable(SometimesFeature):

    @classmethod
    def visible_to(self, user):
        return False


class RestrictableFeatureTestCase(OpalTestCase):

    def test_restricted(self):
        expected = [Available]
        self.assertEqual(expected, list(SometimesFeature.for_user(self.user)))
