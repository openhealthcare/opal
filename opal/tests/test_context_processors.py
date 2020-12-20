"""
Test the opal.context_processors module
"""
from unittest.mock import patch
from django.test import TestCase
from opal import context_processors
from opal.core.subrecords import subrecords


class SettingsTestCase(TestCase):
    @patch("opal.context_processors.s")
    def test_settings(self, s):
        s.some_attribute = 'hello'

        context = context_processors.settings(None)
        self.assertEqual(
            context["some_attribute"], "hello"
        )


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
