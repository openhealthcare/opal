# Opal Episode Detail Views

By defualt, the OPAL core provides each [episode](datamodel.md) with a detail view.

### Template selection

Episode detail templates live in `./templates/detail/*`. In order to select the appropriate
template for a given episode, OPAL looks first for the template for the episode category - so
for `inpatient` episodes, that would be  `detail/inpatient.html`.

### Extending detail/detail_base.html

There is a base template for detail views which you can inherit from -  `detail/detail_base.html`.
This template has the following blocks: 


##### {% block heading %}

The main page heading. Will default to the name of the patient.

##### {% block subheading %}

The page subheading. Will default to the hospital number and DOB of the patient.

##### {% block sidebar_panels %}

Add your own panels to the sidebar

##### {% block left_column %}

The left hand column of the main view.

##### {% block right_column %}

The right hand column of the main view.

### Rendering Record Panels

A frequent pattern when constructing detail views is to render a panel for a particular `Subrecord` 
type. The panels templatetag library contains some useful helpers for rendering panels based on 
models.

    {% load panels %}
    {% record_panel Diagnosis %}

The above code will render a panel for your episode, including the `Subrecord` detail template for
each instance, and allowing editing, deletion and creation of instances of your `Subrecord`. 

You may also consult the Detailed [reference documentation](reference/record_panel_templatetag.md) for 
Record Panels.
