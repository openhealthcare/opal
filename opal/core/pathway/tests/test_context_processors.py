"""
Test the opal.core.pathways.context_processors module
"""
from unittest.mock import patch
from django.test import TestCase
from opal.core.pathway import context_processors
from opal.core.pathway import Pathway

class PathwaysTestCase(TestCase):

    @patch(
        "opal.core.pathway.context_processors.Pathway.list",
        side_effect=ValueError("Check Lazy")
    )
    def test_lazy(self, pathways_patch):
        """ pathway list is lazily evaluated, we can
            check this easily, by raising an error
        """
        context = context_processors.pathways(None)

        with self.assertRaises(ValueError):
            context["pathways"].PagePathwayExample

    def test_pathways_are_populated(self):

        context = context_processors.pathways(None)
        pathways_context = context["pathways"]
        for pathway in Pathway.list():
            pathway_name = pathway.__name__
            found_class = getattr(pathways_context, pathway_name)
            self.assertEqual(found_class, pathway)
