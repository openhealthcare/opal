"""
Unittests for opal.core.lookuplists
"""
from django.contrib.contenttypes.models import ContentType

from opal.core import exceptions
from opal.core.test import OpalTestCase
from opal.models import Synonym
from opal.tests.models import Hat, EtherialHat, GhostHat

from opal.core.lookuplists import (
    load_lookuplist, lookuplists, get_or_create_lookuplist_item,
    load_lookuplist_item
)


# Section 1: Test cases to inherit from

class AbstractLookupListTestCase(OpalTestCase):
    def setUp(self):
        self.hat = Hat.objects.create(name="Cowboy")
        ct = ContentType.objects.get_for_model(Hat)
        Synonym.objects.create(
            content_type=ct,
            object_id=self.hat.id,
            name="Stetson"
        )


class LookupListLoadingTestCase(AbstractLookupListTestCase):
    def test_create_instance(self):
        data = {"hat": [dict(name="Bowler", synonyms=[])]}
        _, created, _ = load_lookuplist(data)
        self.assertEqual(created, 1)


# Section 2: Unittests for module

class GetOrCreateLookuplistItemTestCase(OpalTestCase):

    def test_get_matching_item(self):
        cap = Hat.objects.create(name='Flatcap', code='CAP', system='TLA')
        instance, created = get_or_create_lookuplist_item(
            Hat, name='Flatcap', code='CAP', system='TLA'
        )
        self.assertEqual(False, created)
        self.assertEqual(cap.id, instance.id)
        self.assertEqual('CAP', instance.code)
        self.assertEqual('Flatcap', instance.name)
        self.assertEqual('TLA', instance.system)

    def test_same_code_different_value(self):
        cap = Hat.objects.create(name='Flat cap', code='CAP', system='TLA')
        with self.assertRaises(exceptions.InvalidDataError):
            instance, created = get_or_create_lookuplist_item(
                Hat, name='Baseball cap', code='CAP', system='TLA'
            )

    def test_same_value_no_code(self):
        cap = Hat.objects.create(name='Flat cap')
        instance, created = get_or_create_lookuplist_item(
            Hat, name='Flat cap', code='CAP', system='TLA'
        )
        self.assertEqual(False, created)
        self.assertEqual('CAP', instance.code)
        self.assertEqual('TLA', instance.system)

    def test_dont_treat_none_as_equal_when_it_comes_to_codes(self):
        Hat.objects.create(name='Stovepipe')
        instance, created = get_or_create_lookuplist_item(
            Hat, 'Pork Pie Hat', None, None
        )
        self.assertEqual(True, created)

    def test_new_item(self):
        instance, created = get_or_create_lookuplist_item(
            Hat, name='Pork pie hat', code='PPH', system='TLA'
        )
        self.assertEqual(True, created)
        self.assertEqual(1, Hat.objects.filter(
            name='Pork pie hat', code='PPH', system='TLA'
        ).count())


class LoadLookuplistItemTestCase(OpalTestCase):

    def data(self):
        return {
            'name'    : 'Pork Pie Hat',
            'coding'  : {
                'code'  :'PPH',
                'system': 'TLA'
            },
            'synonyms': [
                "Theme for Lester Young"
            ]
        }

    def test_data_has_no_name(self):
        item = self.data()
        del item['name']
        with self.assertRaises(exceptions.InvalidDataError):
            load_lookuplist_item(Hat, item)

    def test_item_has_coding_without_system(self):
        item = self.data()
        del item['coding']['system']
        with self.assertRaises(exceptions.InvalidDataError):
            load_lookuplist_item(Hat, item)

    def test_item_created_just_name(self):
        item = self.data()
        del item['coding']

        self.assertEqual(0, Hat.objects.filter(name='Pork Pie Hat').count())

        created, synonyms_created = load_lookuplist_item(Hat, item)

        self.assertEqual(1, created)
        self.assertEqual(1, Hat.objects.filter(name='Pork Pie Hat').count())

    def test_item_created_name_and_coding_system(self):
        item = self.data()
        self.assertEqual(0, Hat.objects.filter(name='Pork Pie Hat').count())

        created, synonyms_created = load_lookuplist_item(Hat, item)

        self.assertEqual(1, created)
        self.assertEqual(1, Hat.objects.filter(
            name='Pork Pie Hat', code='PPH', system='TLA'
        ).count())

    def test_synonyms_created(self):
        item = self.data()
        self.assertEqual(0, Hat.objects.filter(name='Pork Pie Hat').count())

        created, synonyms_created = load_lookuplist_item(Hat, item)

        self.assertEqual(1, synonyms_created)

        pph = Hat.objects.get(name='Pork Pie Hat')
        synonyms = pph.synonyms.all()

        self.assertEqual(1, len(synonyms))
        self.assertEqual('Theme for Lester Young', synonyms[0].name)

    def test_create_instance_allow_no_symptom(self):
        data = {"hat": [dict(name="Bowler")]}
        _, created, synonyms = load_lookuplist(data)
        self.assertEqual(created, 1)
        self.assertEqual(synonyms, 0)


class LookupListClassTestCase(AbstractLookupListTestCase):
    def test_str(self):
        self.assertEqual(self.hat.__str__(), u"Cowboy")

    def test_to_dict(self):
        self.assertEqual(self.hat.to_dict(self.user), "Cowboy")

    def test_get_api_name(self):
        self.assertEqual(Hat.get_api_name(), "hat")

    def test_save_with_synonym(self):
        with self.assertRaises(ValueError) as v:
            Hat.objects.create(name="Stetson")

    def test_save_normal(self):
        Hat.objects.create(name="Bowler")
        self.assertTrue(Hat.objects.filter(name="Bowler").exists())


class LookuplistsIteratorTestCase(AbstractLookupListTestCase):
    def test_lookuplists(self):
        all_lists = list(lookuplists())
        self.assertIn(Hat, all_lists)

    def test_ignores_abstract(self):
        """
        ignore models where meta.abstract == true
        """
        all_lists = list(lookuplists())
        self.assertNotIn(EtherialHat, all_lists)

    def test_includes_subclasses_of_abstract_lookuplists(self):
        """
        make sure we include things that don't
        directly inherit from lookup lists
        """
        all_lists = list(lookuplists())
        self.assertIn(GhostHat, all_lists)


class LookupListLoadingTestCase(AbstractLookupListTestCase):
    def test_create_instance(self):
        data = {"hat": [dict(name="Bowler", synonyms=[])]}
        _, created, _ = load_lookuplist(data)
        self.assertEqual(created, 1)

    def test_dont_create_instance(self):
        data = {"hat": [dict(name="Cowboy", synonyms=[])]}
        _, created, _ = load_lookuplist(data)
        self.assertEqual(created, 0)

    def test_create_synonym(self):
        data = {"hat": [dict(name="Cowboy", synonyms=["Ten Gallon"])]}
        _, created, synonyms = load_lookuplist(data)
        self.assertEqual(created, 0)
        self.assertEqual(synonyms, 1)

    def test_dont_create_synonym(self):
        data = {"hat": [dict(name="Cowboy", synonyms=["Stetson"])]}
        _, created, synonyms = load_lookuplist(data)
        self.assertEqual(created, 0)
        self.assertEqual(synonyms, 0)

    def test_create_instance_and_synonym(self):
        data = {"hat": [dict(name="Bowler", synonyms=["Derby"])]}
        _, created, synonyms = load_lookuplist(data)
        self.assertEqual(created, 1)
        self.assertEqual(synonyms, 1)
