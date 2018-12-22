"""
Test util fields
"""
from django.test import TestCase
from six import b

from opal.tests.models import DogOwner, Dog

class FKorFTTest(TestCase):
    def setUp(self):
        self.Model = DogOwner
        self.ll = Dog

    def test_set_none(self):
        # As much as anything this is checking that we *can* set None
        # on a FKorFT field - ensuring a previous bug where .split()
        # was always called on the value does not reappear.
        instance = self.Model()
        instance.dog = None

        self.assertEqual('', instance.dog)
