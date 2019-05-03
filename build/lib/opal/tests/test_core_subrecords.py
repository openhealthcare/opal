"""
Unittests for the opal.core.subrecords module
"""
from opal.core.test import OpalTestCase
from opal.tests import models as tmodels

from opal.core import subrecords


class EpisodeSubrecordsTestCase(OpalTestCase):
    def setUp(self):
        super(EpisodeSubrecordsTestCase, self).setUp()
        self.episode_subrecords = {i for i in subrecords.episode_subrecords()}

    def test_dont_include_patient_subrecords(self):
        self.assertNotIn(tmodels.FamousLastWords, self.episode_subrecords)

    def test_get_episode_subrecords(self):
        self.assertIn(tmodels.HatWearer, self.episode_subrecords)

    def test_dont_include_exclude_from_subrecords(self):
        self.assertNotIn(tmodels.InvisibleHatWearer, self.episode_subrecords)

    def test_dont_include_abstract_subrecords(self):
        self.assertNotIn(tmodels.AbstractHatWearer, self.episode_subrecords)


class PatientSubrecordsTestCase(OpalTestCase):
    def setUp(self):
        super(PatientSubrecordsTestCase, self).setUp()
        self.patient_subrecords = {i for i in subrecords.patient_subrecords()}

    def test_get_patient_subrecords(self):
        self.assertIn(tmodels.FamousLastWords, self.patient_subrecords)

    def test_dont_include_exclude_from_subrecords(self):
        self.assertNotIn(tmodels.InvisibleDog, self.patient_subrecords)

    def test_dont_include_episode_subrecords(self):
        self.assertNotIn(tmodels.HatWearer, self.patient_subrecords)

    def test_dont_include_abstract_subrecords(self):
        self.assertNotIn(tmodels.AbstractDog, self.patient_subrecords)


class SubrecordsTestCase(OpalTestCase):

    def test_subrecords(self):
        all_subrecords = [i for i in subrecords.subrecords()]
        self.assertIn(tmodels.FamousLastWords, all_subrecords)
        self.assertIn(tmodels.HatWearer, all_subrecords)


class SingletonsTestCase(OpalTestCase):

    def test_singletons(self):
        singletons = [i for i in subrecords.singletons()]
        self.assertIn(tmodels.FamousLastWords, singletons)

    def test_non_singletons(self):
        singletons = [i for i in subrecords.singletons()]
        self.assertNotIn(tmodels.HatWearer, singletons)


class GetSubrecordFromAPINameTestCase(OpalTestCase):

    def test_get_get_subrecord_from_api_name(self):
        hatwearer_api_name = tmodels.HatWearer.get_api_name()
        famous_api_name = tmodels.FamousLastWords.get_api_name()
        self.assertEqual(
            tmodels.HatWearer,
            subrecords.get_subrecord_from_api_name(hatwearer_api_name)
        )

        self.assertEqual(
            tmodels.FamousLastWords,
            subrecords.get_subrecord_from_api_name(famous_api_name)
        )

    def test_subrecord_does_not_exist(self):
        with self.assertRaises(ValueError):
            subrecords.get_subrecord_from_api_name('not_a_model')


class GetSubrecordFromModelNameTestCase(OpalTestCase):

    def test_get_get_subrecord_from_model_name(self):
        self.assertEqual(
            tmodels.HatWearer,
            subrecords.get_subrecord_from_model_name("HatWearer")
        )

        self.assertEqual(
            tmodels.FamousLastWords,
            subrecords.get_subrecord_from_model_name("FamousLastWords")
        )

    def test_subrecord_does_not_exist(self):
        with self.assertRaises(ValueError):
            subrecords.get_subrecord_from_model_name('NotAModel')
