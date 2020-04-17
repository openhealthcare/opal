"""
Test the opal.context_processors module
"""
from unittest.mock import patch
from django.test import TestCase
from opal import context_processors
from opal.core.subrecords import subrecords


class SettingsTestCase(TestCase):
    def test_settings(self):
        from django.conf import settings

        context = context_processors.settings(None)

        for s in dir(settings):
            self.assertEqual(getattr(settings, s), context[s])


class ModelsTestCase(TestCase):

    @patch(
        "opal.context_processors.subrecords_iterator",
        side_effect=ValueError("Check Lazy")
    )
    def test_lazy(self, subrecord_iterator_patch):
        """ subrecord is lazily evaluated, we can
            check this easily, by raising an error
        """
        context = context_processors.models(None)

        with self.assertRaises(ValueError):
            context["models"].Demograpics

    def test_subrecords_are_populated(self):
        context = context_processors.models(None)
        subrecord_context = context["models"]
        for subrecord in subrecords():
            name = subrecord.__name__
            found_class = getattr(subrecord_context, name)
            self.assertEqual(found_class, subrecord)
