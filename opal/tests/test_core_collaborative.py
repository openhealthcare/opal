"""
Unittests for opal.core.collaborative
"""
from django.test import TestCase

from opal.core import collaborative

class CollaborativePluginTestCase(TestCase):
    def test_javascripts(self):
        expected = ['js/collaborative/phoenix.js']
        javascripts = collaborative.CollaborativePlugin.javascripts
        self.assertEqual(expected, javascripts['opal.upstream.deps'])
