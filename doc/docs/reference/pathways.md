# Pathway
Opal comes with a method of building complicated forms.

In the simplest case this is just listing a number of models in a pathway in a file called `{{ your app }}/pathways.py`
like so:

```python
import opal.core import pathway
from myapp import models
class SimplePathway(pathway.PagePathway):
    display_name = 'A simple pathway'
    slug = "simples"
    steps        = (
        models.Demographics,
        models.PastMedicalHistory
    )
```

 This will give you file at `http://localhost:8000/pathway/#/simples` that
 lets the user create a patient with their demographics and past medical history


## Customisation
* [Loading data from Existing Episodes](#loading-data-from-existing-episodes)
* [Customising server side logic](#customising-the-server-side-logic)
* [Multiple instances of records](#multiple-instances-of-records)
* [Validation](#validation)
* [Wizards](#wizards)
* [Complex steps](#complex-steps)
* [Success Redirects](#success-redirects)


### Loading Data From Existing Episodes

A URL without a patient id or episode id will create a new patent/episode when
you save it.

To update a particular patient with a new episode, the URL should be:
`http://localhost:8000/pathway/#/simples/{{ patient_id }}`

To update a particular episode the URL should be:
`http://localhost:8000/pathway/#/simples/{{ patient_id }}/{{ episode_id }}`

When you load from these urls, your forms will come prepulated with the
existing data for that patient/episode.


### Customising The Server-side Logic

If you want to add any custom save logic for your step, you can put in a `pre_save` method. This is passed the full data dictionary that has been received from the client and the patient and episode that the pathways been saved for, if they exist (If you're saving a pathway for a new patient/episode, they won't have been created at this time).


### Multiple Instances Of Records

If the model is not a singleton, by default it will be show in the form as
a multiple section that allows the user to add one or more models.

This displays a delete button for existing subrecords.

By default, any subrecords that are deleted, or are not included in the data sent back
to the server are deleted.

If you don't wish this to happen, pass `delete_others=False` to the `MultiSaveStep`.

```python
import pathway
from myapp import models

class SimplePathway(pathway.Pathway):
    display_name = 'A simple pathway'
    slug         = 'simples'
    steps        = (
        pathways.MultiSaveStep(model=models.Allergies, delete_others=True),
        models.Treatment,
        models.PastMedicalHistory
    )
```

In this case, the pathway will delete any existing instances of the given Subrecord Model that
are not sent back to the API in the JSON data.

### Complex Steps

If we want to save multiple types of subrecords at the same step, we can do that by including the
relevant form templates in a custom step template.

```python
import pathway
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

Note pathways created in this way will not add in the model defaults.


#### Complex step logic
  Pathway steps can be injected with a custom controller. You can do this by declaring an angular step in your controller.

  for example

  ```python
  steps = (
    Step(
        model="NyModel",
        step_controller="FindPatientCtrl",
    ),
  ```

  Your javascript controller should then look something like...

  ```js
  angular.module('opal.controllers').controller('FindPatientCtrl',
    function(scope, step, episode) {
      "use strict";
      // your custom logic
  });
  ```

  The scope passed in comes fully loaded with reference data and meta data.
  It also comes with the scope.editing. This is the dictionary that will
  appear in the form and will be saved back at the end.

  The step is the step definition from the server, ie the output of
  step.to_dict.

  The episode is the episode in its display state, before its been changed
  into a state that is ready to be displayed in the form.

  steps can declare optional `preSave` method on their scope. This is passed
  the editing dictionary which will then be saved and can be altered in place
  if necessary.



#### Complex Steps With Multiple Instances Per Subrecord

If we need to also save multiple types of the same subrecord e.g. `Treatment` in this step,
we simply use the `multisave` template tag.

```html
{% load pathways %}

{% include models.Demographics.get_form_template %}
{% include models.Diagnosis.get_form_template %}
{% multisave models.Treatment %}
```

Alternatively you may want to create your own multisave step forms, you can use the multi-save-wrapper for this.

```html

<div save-multiple-wrapper="editing.treatment">
  <div ng-repeat="editing in model.subrecords">
    {% input field="Treatment.drug" %}
    <button ng-click="remove($index)"></button>
  </div>

  <button ng-click="addAnother()"></button>
</div>
```

#### Complex Steps With Custom Javascript Logic

We can pass in custom controllers to individual steps. Custom
controllers are sandboxed, they share scope.editing with other scopes but nothing else. They come prefilled with the defaults that you need. They are passed scope, step and episode.

The scope is the already preloaded with metadata and all the lookup lists so you that's already done for you.

scope.editing is also populated. If the subrecord is a singleton (ie with _is_singleton=True), its populated as an object. Otherwise it comes through to the custom controller and scope as an array of subrecords which is empty if there isn't one.

for example to make a service available in the template for a step, and only in that step

```js
angular.module('opal.controllers').controller('AddResultsCtrl',
function(scope, step, episode, someService) {
    "use strict";

    scope.someService = someService
});
```

`scope.editing is shared between all the steps` and its what is sent back to the server at the end.

If you want to change any data before its sent back to the server you add a function called `preSave` on the scope. This is passed scope.editing.


### Validation

If you want to add custom validation, there is an `valid(form)` called to each step controller. This means you can set validation rules on the form. An invalid form will have the save button disabled, until the form is valid.


### Wizards

Wizard pathways look for a `hideFooter` variable that defaults to false. If set to true, this will hide the default next/save button. If you don't want the wizard pathway to be a linear progression, ie you want the user to go to different
steps based on options they chose. This is a handy option for you.

If you want to handle complex order, this is best done in a custom controller
for you step class. You can set this with.

### Success Redirects

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

#### Redirect Mixins

By default any full page pathway (ie not a modal) will redirect to the episode
detail view of that episode.

If you do not wish this to be the case you can override the redirect_url.

Pathways comes with the RedirectsToPatientMixin, which redirects to the Patient
detail view and can be used as follows.


```python
from pathways import RedirectsToPatientMixin

class PatientRedirectPathway(pathway.RedirectsToPatientMixin, pathway.PagePathway):
    display_name = 'Redirector example Pathway'
    steps = (...)
```

##### pathways.RedirectsToPatientMixin

Redirect to the patient detail page for this patient.


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

e.g.

```html
<a open-pathway="test_results"
   pathway-episode="someOtherEpisode"
   pathway-callback="refreshEpisode(episode_id)">
   open test results pathway
</a>

```


#### Pathway.Pathway. _attributes_

##### Pathway.display_name

The human readable display name for this pathway. Will be used in the base template for
full page pathways.

##### Pathway.slug

The slug to use in the URL for accessing an individual pathway, and the string that can
be passed to `Pathway.get()` that will return i.t

##### Pathway.steps

The steps that make up this pathway. A tuple of either `opal.models.Subrecord` or
`pathway.Step` subclasses.

###### Patway.pathway_service

The Service that is used to instantiate the pathway. This should inherit from the Pathway js service.


###### Patway.pathway_insert

The name of the class that you're replaceing with the pathway template. You probably shouldn't have to change this.

###### Patway.template
The name of the pathway template, it must include a div/span with the class .to_append which will be replaced by the wrapped step templates.

###### Patway.modal_template

If set, this template will be used if your pathway is opened in a modal. If its not set the template attribute will be used.


#### Pathway. _methods_

##### Pathway.redirect_url(self, patient, episde)

Returns a string that we should redirect to on success. Defaults to
an episode detail screen

##### pathways.RedirectsToPatientMixin

Redirect to the patient detail page for this patient.
he patient detail page, viewing the last episode for this patient.

##### Pathway.save(user=None, episode=None, patient=None)

Saves a pathway, it removes items that haven't changed and then
saves with the Patient.bulk_update method
