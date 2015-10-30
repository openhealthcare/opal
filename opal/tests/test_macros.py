from django.test import TestCase

from opal.models import Macro

class MacroTest(TestCase):
    def setUp(self):
        self.m1 = Macro(title="hai", expanded="Why Hello there!")
        self.m2 = Macro(title="brb", expanded="Be right back...")
        self.m1.save()
        self.m2.save()

    def tearDown(self):
        for m in Macro.objects.all():
            m.delete()

    def test_to_dict(self):
        serialised = [
            dict(label="hai", expanded="Why Hello there!",),
            dict(label="brb", expanded="Be right back...")
        ]
        self.assertEqual(serialised, Macro.to_dict())
