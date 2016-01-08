"""
Test the opal.context_processors module
"""
from django.test import TestCase

from opal import context_processors

class SettingsTestCase(TestCase):
    def test_settings(self):
        from django.conf import settings

        context = context_processors.settings(None)

        for s in dir(settings):
            self.assertEqual(getattr(settings, s), context[s])
