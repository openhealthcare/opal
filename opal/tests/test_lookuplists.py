from opal.core.test import OpalTestCase
from opal.models import Synonym
from opal.tests.models import Hat
from django.contrib.contenttypes.models import ContentType


class LookupListTestCase(OpalTestCase):

    def setUp(self):
        self.hat = Hat.objects.create(name="Cowboy")
        ct = ContentType.objects.get_for_model(Hat)
        Synonym.objects.create(
            content_type=ct,
            object_id=self.hat.id,
            name="Stetson"
        )

    def test_unicode(self):
        self.assertEqual(unicode(self.hat), "Cowboy")

    def test_to_dict(self):
        self.assertEqual(self.hat.to_dict(self.user), "Cowboy")

    def test_get_api_name(self):
        self.assertEqual(Hat.get_api_name(), "hat")

    def test_save_with_synonym(self):
        with self.assertRaises(ValueError) as v:
            Hat.objects.create(name="Stetson")

        self.assertEqual(
            v.exception.message,
            'Hat, or a synonym of one, already exists with the name Stetson'
        )

    def test_save_normal(self):
        Hat.objects.create(name="Bowler")
        self.assertTrue(Hat.objects.filter(name="Bowler").exists())
