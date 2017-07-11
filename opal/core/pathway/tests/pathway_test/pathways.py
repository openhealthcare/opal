from opal.core.pathway import pathways, steps

from opal.tests import models as test_models


class SomeComplicatedStep(steps.Step):
    display_name = "Some complicated step"
    step_controller = "SomeController"
    template = "Sometemplate.html"


class PagePathwayExample(pathways.PagePathway):
    display_name = "Dog Owner"
    slug = 'dog_owner'
    icon = "fa fa-something"

    steps = (
        test_models.FamousLastWords,
        steps.Step(model=test_models.DogOwner),
        test_models.Colour,
        SomeComplicatedStep()
    )


class WizardPathwayExample(pathways.WizardPathway):
    display_name = "colour"
    slug = 'colour'
    icon = "fa fa-something"

    steps = (
        test_models.Colour,
    )
