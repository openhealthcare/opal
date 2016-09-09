# Form Helpers

OPAL comes with a selection of templatetags that can help you with the
repetitive task of generating Bootstrap and OPAL compatible markup for
your forms.


### {% checkbox ... %}

Generates a checkbox

Keywords:

* `field` a string of the model name '.' field from this it calculates the label, model and will infer the lookuplist if required. For example {% checkbox field="DogOwner.dog" %}
* `label` The Label with which to describe this field
* `model` The model which we are editing (This is a string that references an in-scope Angular variable)
* `disabled` If this exists, we use this as the expression for the ng-disabled directive

### {% datepicker ... %}

Generates a datepicker

Keywords:

* `field` a string of the models api name '.' field from this it calculates the label, model and will infer the lookuplist if required. For example {% datepicker field="DogOwner.dog" %}
* `label` The Label with which to describe this field
* `model` The model which we are editing (This is a string that references an in-scope Angular variable)
* `show`  A string that contains an Angular expression for the ng-show directive
* `hide`  A string that contains an Angular expression for the ng-hide directive
* `required` Label to show when we're required

### {% datepicker ... %}

Generates a date time fields, a date field on one line and a time field on another

Keywords:

* `field` a string of the models api name '.' field from this it calculates the label, model and will infer the lookuplist if required. For example {% datetimepicker field="DogOwner.vet_appointment" %}
* `date_label` The Label with which to describe the date field (defaults to 'Date')
* `time_label` The Label with which to describe the date field (defaults to 'Time')
* `model` The model which we are editing (This is a string that references an in-scope Angular variable)
* `change`  an angular directive that fires on change



### {% input ... %}

The input template tag generates you a form input that will play nicely with OPAL's styling.

Keywords:

* `field` a string of the models api name '.' field from this it calculates the label, model and will infer the lookuplist if required. For example {% input field="DogOwner.dog" %}
* `label` The Label with which to describe this field
* `model` The model which we are editing (This is a string that references an in-scope Angular variable)
* `show`  A string that contains an Angular expression for the ng-show directive
* `hide`  A string that contains an Angular expression for the ng-hide directive
* `lookuplist` an Angular expression that evaluates to an array containing the lookuplist values
* `required` Label to show when we're required
* `enter` expression to evaluate if the user presses return when in this input
* `maxlength` maximum number of characters for this input. Will render the form invalid and display help text if exceeded.

#### Inputs for subrecord fields

A very common pattern is to render form fields that relate to fields of `Subrecords`. The input templatetag
accepts a `field` argument, from which it will infer the label, model and lookuplist by introspecting the relevant subrecord model.

    {% input field="allergies.drug" %}

#### Inputs with units

We also often want to display the unit of a particular field to help our users - consistent styling for this is
available by using the unit argument e.g.

```html
{% input label="Weight" model="editing.weight" unit="kg" %}
```

### {% radio ... %}

Generates an inline radio input

Keywords:

* `field` a string of the models api name '.' field from this it calculates the label, model and will infer the lookuplist if required. For example {% radio field="DogOwner.dog" %}
* `label` The Label with which to describe this input
* `model` The model which we are editing (This is a string that references an in-scope Angular variable)
* `show`  A string that contains an Angular expression for the ng-show directive
* `hide`  A string that contains an Angular expression for the ng-hide directive
* `lookuplist` an Angular expression that evaluates to an array containing the radio values

### {% select ... %}

Generates an inline select input

Keywords:

* `field` a string of the models api name '.' field from this it calculates the label, model and will infer the lookuplist if required. For example {% select field="DogOwner.dog" %}
* `label` The Label with which to describe this input
* `model` The model which we are editing (This is a string that references an in-scope Angular variable)
* `show`  A string that contains an Angular expression for the ng-show directive
* `hide`  A string that contains an Angular expression for the ng-hide directive
* `lookuplist` an Angular expression that evaluates to an array containing the radio values
* `other` A boolean parameter that if true, provides a free text option when 'Other' is selected
* `help` a template to use as the contents of a help popover
* `static` an Angular expression that will swap the display to be a static input if it evaluates to `true`
*

### {% textarea ... %}

Generates an inline textarea input

Keywords:

* `field` a string of the models api name '.' field from this it calculates the label, model and will infer the lookuplist if required. For example {% textarea field="DogOwner.dog" %}
* `label` The Label with which to describe this input
* `model` The model which we are editing (This is a string that references an in-scope Angular variable)
* `show`  A string that contains an Angular expression for the ng-show directive
* `hide`  A string that contains an Angular expression for the ng-hide directive


### {% static ... %}

Generates a bootstrap Static div (for displaying data from fields as uneditable but formatted nicely with appropriate styles).

Takes one positional argument, a string representing the subrecord field path.


    {% static "Demographics.name" %}
    <!-- Renders as -->
    <div class="form-group">
      <label class="control-label col-sm-3">
        Name
      </label>
      <p class="form-control-static col-sm-8">
        [[ editing.demographics.name ]]
      </p>
    </div>


### {% icon "icon-name" %}

Renders a Bootstrap style Icon tag.
If the icon starts with `fa` or `glyphicon` then we will insert the preceding `fa`.

    {% icon "fa-user-md" %}
    <i class="fa fa-user-md"></i>

    {% icon "cusom-icon"}
    <i class="custom-icon"></i>
