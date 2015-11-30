"""
Test util fields
"""
from django.db import models
from django.test import TestCase

from opal.core.fields import ForeignKeyOrFreeText
from opal.core import lookuplists

class FKorFTTest(TestCase):
    def setUp(self):
        class LookupList(lookuplists.LookupList): pass

        class Model(models.Model):
            field = ForeignKeyOrFreeText(LookupList)

        self.Model = Model
        self.ll = LookupList

    def test_set_none(self):
        # As much as anything this is checking that we *can* set None
        # on a FKorFT field - ensuring a previous bug where .split()
        # was always called on the value does not reappear.
        instance = self.Model()
        instance.field = None
        self.assertEqual('', instance.field)
