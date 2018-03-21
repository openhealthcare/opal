# Reference docs: `opal.core.pathway`

## Pathway

Pathway is the base class for most complex forms in Opal applications.

### Attributes

#### Pathway.display_name

The human readable display name for this pathway. Will be used in the base template for
full page pathways.

#### Pathway.slug

The slug to use in the URL for accessing an individual pathway, and the string that can
be passed to `Pathway.get()` that will return it.

#### Pathway.steps

The steps that make up this pathway. A tuple of either `opal.models.Subrecord` or
`pathway.Step` subclasses.

#### Pathway.pathway_service

The Service that is used to instantiate the pathway. This should inherit from the Pathway js service.


#### Pathway.pathway_insert

The name of the class that you're replaceing with the pathway template. You probably shouldn't have to change this.

#### Pathway.template
The name of the pathway template, it must include a div/span with the class .to_append which will be replaced by the wrapped step templates.

#### Pathway.modal_template

If set, this template will be used if your pathway is opened in a modal. If its not set the template attribute will be used.

### Methods

#### `Pathway.redirect_url(self, patient, episde)`

Returns a string that we should redirect to on success. Defaults to
an episode detail screen

#### `Pathway.save(user=None, episode=None, patient=None)`

Saves a pathway, it removes items that haven't changed and then
saves with the Patient.bulk_update method

## WizardPathway

Inherits from `opal.core.pathway.Pathway`, this displays one step per page, with `next` and `back` buttons
to navigate through the form.

## PagePathway

Inherits from `opal.core.pathway.Pathway`, this displays all steps as one long form.

## Step

Steps are a single section within a form, and can be instances of either `opal.models.Subrecord` or
`pathway.Step` subclasses. You can use both types of Step in a given Pathway.

More detail on Steps is given in the [Guides section on Pathways](../guides/pathways.md)
        
## HelpTextStep

A Step subclass with help text to the side of the form

## FindPatientStep

A frequent pattern is a form that allows the user to search for a patient at the start. This step
includes a widget for searching for patients, then selecting that patient for use in the rest of the
form.

## RedirectsToPatientMixin

After saving, redirect the browser to the patient detail page for the relevant patient.
