from __future__ import unicode_literals

from opal.core.test import OpalTestCase
from django.core.urlresolvers import reverse
from opal.tests import models as test_models

from opal.core.pathway import Step, HelpTextStep, PagePathway
from opal.core.pathway.steps import InitializationError
from opal.core.pathway.tests.pathway_test.pathways import SomeComplicatedStep


class StepTestCase(OpalTestCase):

    def test_step_cant_be_multiple_without_a_model(self):
        with self.assertRaises(InitializationError):
            Step(multiple=True)

    def test_to_dict_model_passed_in(self):
        step_dict = Step(model=test_models.Colour).to_dict()
        self.assertEqual(
            step_dict["display_name"], "Colour",
        )
        self.assertEqual(
            step_dict["icon"], "fa fa-comments"
        )
        self.assertEqual(
            step_dict["api_name"], "colour"
        )
        self.assertEqual(
            step_dict["model_api_name"], "colour"
        )

    def test_to_dict_args_passed_in(self):
        step_dict = Step(
            display_name="Some Step",
            icon="fa fa-some-step",
            api_name="some_step",
            model_api_name="some_model_api_step",
            template="some_template.html",
            step_controller="somewhere"
        ).to_dict()
        self.assertEqual(
            step_dict["display_name"], "Some Step",
        )
        self.assertEqual(
            step_dict["icon"], "fa fa-some-step"
        )
        self.assertEqual(
            step_dict["api_name"], "some_step"
        )
        self.assertEqual(
            step_dict["model_api_name"], "some_model_api_step"
        )
        self.assertEqual(
            step_dict["step_controller"], "somewhere"
        )

    def test_arguments_passed_in_overide_model(self):
        step_dict = Step(
            model=test_models.Colour,
            display_name="Some Step",
            icon="fa fa-some-step",
            api_name="some_step",
            model_api_name="some_model_api_step",
            template="some_template.html"
        ).to_dict()
        self.assertEqual(
            step_dict["display_name"], "Some Step",
        )
        self.assertEqual(
            step_dict["icon"], "fa fa-some-step"
        )
        self.assertEqual(
            step_dict["api_name"], "some_step"
        )
        self.assertEqual(
            step_dict["model_api_name"], "some_model_api_step"
        )

    def test_to_dict_use_class_attributes(self):
        expected = dict(
            api_name="somecomplicatedstep",
            display_name="Some complicated step",
            step_controller="SomeController",
            icon=None,
            model_api_name=None,
        )
        self.assertEqual(
            SomeComplicatedStep().to_dict(),
            expected
        )

    def test_no_display_name(self):
        with self.assertRaises(InitializationError) as er:
            Step(
                template="some_template.html"
            )
        self.assertEqual(
            str(er.exception), "A step needs either a display_name or a model"
        )

    def test_no_template(self):
        with self.assertRaises(InitializationError) as er:
            Step(
                display_name="no template"
            )
        self.assertEqual(
            str(er.exception), "A step needs either a template or a model"
        )


class HelpTextStepTestCase(OpalTestCase):
    def test_get_help_text(self):
        s = HelpTextStep(
            display_name="fake", template="", help_text=" interesting "
        )
        self.assertEqual(
            s.get_help_text(), "interesting"
        )

    def test_step_render(self):
        class SomePathway(PagePathway):
            display_name = "some pathway"
            slug = "some_pathway"
            steps = (
                HelpTextStep(
                    display_name="fake", template="", help_text=" interesting "
                ),
            )
        url = reverse("pathway_template", kwargs=dict(name="some_pathway"))
        self.assertStatusCode(url, 200)
