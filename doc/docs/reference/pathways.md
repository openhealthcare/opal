# opal.core.pathway

##### pathways.RedirectsToPatientMixin

Redirect to the patient detail page for this patient.

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

###### Pathway.template
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
