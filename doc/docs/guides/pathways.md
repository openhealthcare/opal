# Guide: The pathway module

The pathway module provides developers with a highly extensible method of
working with complex forms.

Typically pathways are forms that allow the user to enter information that spans multiple
`Subrecords` - which can be challenging with the `Subrecord forms`.

The pathway provides Wizards, long multi-model forms, custom validation and much more,
all usable either in full page or modal contexts.

If you're new to using pathways, you might like to go through the
[Pathway tutorial](../tutorials/pathway_tutorial.md).

<blockquote><small>
See the
<a href="../../reference/pathways/">Pathway reference documentation</a>
for detailed class and method level information <br/ >
on the pathway module.
</small></blockquote>

## Pathway steps

A pathway is comprised of a sequence of `Step`s. These are sections within a form.

They can be defined as HTML forms with custom attributes and Angular controllers,
or inferred by passing models to the `steps` attribute of your pathway.

In the simplest case a pathway re-uses the forms for a sequence of subrecords, and we would
create one by subclassing `opal.core.pathway.PagePathway` in a file called
`{{ your app }}/pathways.py` like so:

```python
from opal.core import pathway
from myapp import models

class SimplePathway(pathway.PagePathway):
    display_name = 'A simple pathway'
    slug = "simples"
    steps        = (
        models.Demographics,
        models.PastMedicalHistory
    )
```

This will give you form at `http://localhost:8000/pathway/#/simples` that
lets the user create a patient with their demographics and past medical history

## Customising Steps

When passed a model, a step will infer the details of form templates, display names et
cetera from the subrecord. However a model is not required - you can also pass arbitrary
chunks of html with the two required fields:

``` python
Step(
  template="pathway/steps/my_step.html"
  display_name="My Display Only Step"
)
```

Alternatively, you can override any fields that it would usually take from the model.
The below example, will override the template and not just use the Demographics form template.

``` python
Step(
  template="pathway/steps/my_step.html"
  model=Demographics
)
```

The `Step.base_template` wraps the form template for each step.

By default this is a bootstrap panel,
with the step display name and step icon in the header and the form template in the panel body.

You can override this by overriding the `base_template`.
``` python
Step(
  base_template="pathway/steps/addicted_to_base.html"
  model=Demographics
)
```

If you want to add any custom save logic for your step, you can put in a `pre_save` method.
This is passed the full data dictionary that has been received from the client and the patient
and episode that the pathways been saved for, if they exist (If you're saving a pathway for a
new patient/episode, they won't have been created at this time).

## Loading Data From Existing Episodes

A URL without a patient id or episode id will create a new patent/episode when
you save it.

To update a particular patient with a new episode, the URL should be:
`http://localhost:8000/pathway/#/simples/{{ patient_id }}`

To update a particular episode the URL should be:
`http://localhost:8000/pathway/#/simples/{{ patient_id }}/{{ episode_id }}`

When you visit these urls with the ids for existing patients and episodes,
the form will be prepulated with the existing data for that patient/episode.



## Multiple Instances Of Records

If the model is not a singleton, by default it will be show in the form as
a multiple section that allows the user to add one or more models.

If you don't wish this to happen, pass `multiple=False` to the Step

This displays a delete button for existing subrecords.

By default, any subrecords that are deleted, or are not included in the data sent back
to the server are deleted.

If you don't wish this to happen, pass `delete_others=False` to the Step.

```python
from opal.core import pathway
from myapp import models

class SimplePathway(pathway.Pathway):
    display_name = 'A simple pathway'
    slug         = 'simples'
    steps        = (
        pathway.Step(model=models.Allergies, delete_others=True),
        models.Treatment,
        models.PastMedicalHistory
    )
```

In this case, the pathway will delete any existing instances of the given Subrecord Model that
are not sent back to the API in the JSON data.


## Complex Steps

If we want to save multiple types of subrecords at the same step, we can do that by including the
relevant form templates in a custom step template.

```python
from opal.core import pathway
from myapp import models

class SimplePathway(pathway.Pathway):
    display_name = 'A simple pathway'
    slug         = 'simples'
    steps        = (
        pathways.Step(
            display_name='Demographics and Diagnosis',
            icon='fa fa-clock',
            template='pathways/demographics_and_diagnosis_step.html'
            ),
    )
```

The display name and icon are rendered in the header for this step in your pathway, which
exist outside the scope of the step template itself. Then all we would need is the template
itself:

```html
<!-- pathways/demographics_and_diagnosis_step.html -->
{% include models.Demographics.get_form_template %}
{% include models.Diagnosis.get_form_template %}
```

<blockquote><small>
Pathways created in this way will not add in the model defaults.
</small></blockquote>


## Complex step logic

Pathway steps can be rendered with a custom controller.
You can do this by declaring an angular step in your controller.

```python
steps = (
    Step(
        model=MyModel,
        step_controller="FindPatientCtrl",
    ),
)
```

Your javascript controller should then look something like...

```js
angular.module('opal.controllers').controller('FindPatientCtrl',
    function(scope, step, episode) {
    "use strict";
    // your custom logic
});
```

oWe can pass in custom controllers to individual steps. Custom
controllers are sandboxed, they share `scope.editing` with other scopes but
nothing else.

The scope passed in comes with reference data and meta data set as attributes.
It also comes with the scope.editing. This is the dictionary that will
appear in the form and will be saved back at the end.

The step is the step definition from the server - the output of
`step.to_dict`.

The `episode` is an instance of the javascript Episode class - not the output
of `Episode.makeCopy()`.

Before a copy of the form data is sent back to the server, it is passed to the
`preSave` method of each step controller. Step controllers may alter this data
here if required to e.g. add implicit data points not contained in the form.


## Complex Steps With Multiple Instances Per Subrecord

If we need to also save multiple types of the same subrecord e.g. `Treatment` in this step,
we simply use the `multisave` template tag.

```html
{% load pathways %}

{% include models.Demographics.get_form_template %}
{% include models.Diagnosis.get_form_template %}
{% multisave models.Treatment %}
```

Alternatively you may want to create your own multisave step forms, you can use the
directive `multi-save-wrapper` for this.

```html

<div save-multiple-wrapper="editing.treatment">
  <div ng-repeat="editing in model.subrecords">
    {% input field="Treatment.drug" %}
    <button ng-click="remove($index)"></button>
  </div>

  <button ng-click="addAnother()"></button>
</div>
```

## Validation

If you want to add custom validation, the method `StepController.valid(form)` is
called on each step controller.

This means you can set validation rules on the form.

An invalid form will have the save button disabled, until the form is valid.


## Wizards

Wizard pathways look for a `hideFooter` variable that defaults to false. If set to true, this will hide the default next/save button. If you don't want the wizard pathway to be a linear progression.
This is useful when you want the user to go to different
steps based on options they chose.

If you want to handle complex order, this is best done in a custom controller
for you step class. You can set this with.

## Success Redirects

Often, after successfully saving a pathway, we want to redirect the user to a different
URL - we do this by overriding the `redirect_url` method on the pathway. For example -
to create a pathway that always logged the user out after a successful save:

```python
class LogoutPathway(pathway.Pathway):
    display_name = 'Logout-O-Matic'
    steps        = (...)

    def redirect_url(self, patient):
        return '/accounts/logout/'
```

## Redirect Mixins

By default any full page pathway (ie not a modal) will redirect to the episode
detail view of that episode.

If you do not wish this to be the case you can override the redirect_url.

Pathways comes with the `RedirectsToPatientMixin`, which redirects to the Patient
detail view and can be used as follows.


```python
from opal.core.pathway import RedirectsToPatientMixin

class PatientRedirectPathway(pathway.RedirectsToPatientMixin, pathway.PagePathway):
    display_name = 'Redirector example Pathway'
    steps = (...)
```

## Modal Pathways

Pathways detect when you're opening a pathway from a modal.

You can use a different template for your modal pathway by adding a modal_template attribute to your pathway

Pathways ships with a no footer modal template, the same as the normal modal template but it doesn't display the section at the bottom with the save/cancel button.

To open a modal pathway in a template you can use the open-pathway directive:

```html
<a open-pathway="test_results">open test results pathway</a>
```

The open-pathway directive also includes an optional callback, that is called with the context of the result of the modal.save method, ie episode_id, patient_id and redirect_url.

By default the pathway is opened with whichever episode is on $scope.episode, you can use pathway-episode to define a different episode.


```html
<a open-pathway="test_results"
   pathway-episode="someOtherEpisode"
   pathway-callback="refreshEpisode(episode_id)">
   open test results pathway
</a>

```
