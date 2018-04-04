# Form Helpers

Opal comes with a selection of templatetags that can help you with the
repetitive task of generating Bootstrap and Opal compatible markup for
your forms.

To use these in your HTML templates you need to load them:

```html
<!-- myapp/templates/forms/mytemplate.html -->
{% load forms %}
...
```

### {% checkbox ... %}

Generates a checkbox

Keywords:

* `field` a string of the models api name '.' field which infers attributes for the model, for more information see
[Inference from subrecord fields](#inference-from-subrecord-fields)
* `label` The Label with which to describe this field
* `model` The model which we are editing (This is a string that references an in-scope Angular variable)
* `change`  A javascript function that fires if the field has changed
* `disabled` If this exists, we use this as the expression for the ng-disabled directive
* `element_name` If this exists this is an Angular expression that is set to the 'name' attribute of the html element
* `style` The form style to render this widget with. Possible values are `['horizontal', 'vertical']`. Defaults to 'horizontal'

### {% datepicker ... %}

Generates a datepicker

Keywords:

* `field` a string of the models api name '.' field which infers attributes for the model, for more information see
[Inference from subrecord fields](#inference-from-subrecord-fields)
* `label` The Label with which to describe this field
* `model` The model which we are editing (This is a string that references an in-scope Angular variable)
* `change`  A javascript function that fires if the field has changed
* `show`  A string that contains an Angular expression for the ng-show directive
* `hide`  A string that contains an Angular expression for the ng-hide directive
* `required` Label to show when we're required
* `mindate` Angular Javascript expression to return the minimum possible date
* `element_name` If this exists this is an Angular expression that is set to the 'name' attribute of the html element
* `style` The form style to render this widget with. Possible values are `['horizontal', 'vertical']`. Defaults to 'horizontal'


### {% timepicker ... %}

Generates a time picker widget

Keywords:

* `field` a string of the models api name '.' field which infers attributes for the model, for more information see
[Inference from subrecord fields](#inference-from-subrecord-fields)
* `label` The Label with which to describe the date field (defaults to 'Date')
* `model` The model which we are editing (This is a string that references an in-scope Angular variable)
* `change`  A javascript function that fires if the field has changed
* `style` The form style to render this widget with. Possible values are `['horizontal', 'vertical']`. Defaults to 'horizontal'


### {% datetimepicker ... %}

Generates a date time fields, a date field on one line and a time field on another

Keywords:

* `field` a string of the models api name '.' field which infers attributes for the model, for more information see
[Inference from subrecord fields](#inference-from-subrecord-fields)
* `date_label` The Label with which to describe the date field (defaults to 'Date')
* `time_label` The Label with which to describe the date field (defaults to 'Time')
* `model` The model which we are editing (This is a string that references an in-scope Angular variable)
* `change`  A javascript function that fires if the field has changed
* `element_name` If this exists this is an Angular expression that is set to the 'name' attribute of the html datetime picker element
* `style` The form style to render this widget with. Possible values are `['horizontal', 'vertical']`. Defaults to 'horizontal'


### {% input ... %}

The input template tag generates you a form input that will play nicely with Opal's styling.

Keywords:

* `field` a string of the models api name '.' field which infers attributes for the model, for more information see
[Inference from subrecord fields](#inference-from-subrecord-fields)
* `label` The Label with which to describe this field
* `model` The model which we are editing (This is a string that references an in-scope Angular variable)
* `change`  A javascript function that fires if the field has changed
* `show`  A string that contains an Angular expression for the ng-show directive
* `hide`  A string that contains an Angular expression for the ng-hide directive
* `lookuplist` an Angular expression that evaluates to an array containing the lookuplist values
* `required` Label to show when we're required
* `enter` expression to evaluate if the user presses return when in this input
* `maxlength` maximum number of characters for this input. Will render the form invalid and display help text if exceeded.
* `element_name` If this exists this is an Angular expression that is set to the 'name' attribute of the html element
* `element_type` If this exists it sets the input 'type' on the html tag. For numeric fields set by the 'field' parameter this will default to number. Otherwise it will just default to 'text'.
* `style` The form style to render this widget with. Possible values are `['horizontal', 'vertical']`. Defaults to 'horizontal'


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
* `change`  A javascript function that fires if the field has changed
* `show`  A string that contains an Angular expression for the ng-show directive
* `hide`  A string that contains an Angular expression for the ng-hide directive
* `lookuplist` an Angular expression that evaluates to an array containing the radio values
* `element_name` If this exists this is an Angular expression that is set to the 'name' attribute of the html element
* `style` The form style to render this widget with. Possible values are `['horizontal', 'vertical']`. Defaults to 'horizontal'


### {% select ... %}

Generates an inline select input

Keywords:

* `field` a string of the models api name '.' field from this it calculates the label, model and will infer the lookuplist if required. For example {% select field="DogOwner.dog" %}
* `label` The Label with which to describe this input
* `model` The model which we are editing (This is a string that references an in-scope Angular variable)
*  `change`  A javascript function that fires if the field has changed
* `show`  A string that contains an Angular expression for the ng-show directive
* `hide`  A string that contains an Angular expression for the ng-hide directive
* `lookuplist` an Angular expression that evaluates to an array containing the radio values
* `other` A boolean parameter that if true, provides a free text option when 'Other' is selected
* `help` a template to use as the contents of a help popover
* `static` an Angular expression that will swap the display to be a static input if it evaluates to `true`
* `element_name` If this exists this is an Angular expression that is set to the 'name' attribute of the html element*
* `style` The form style to render this widget with. Possible values are `['horizontal', 'vertical']`. Defaults to 'horizontal'

### {% textarea ... %}

Generates an inline textarea input

Keywords:

* `field` a string of the models api name '.' field from this it calculates the label, model and will infer the lookuplist if required. For example {% textarea field="DogOwner.dog" %}
* `label` The Label with which to describe this input
* `model` The model which we are editing (This is a string that references an in-scope Angular variable)
*  `change`  A javascript function that fires if the field has changed
* `show`  A string that contains an Angular expression for the ng-show directive
* `hide`  A string that contains an Angular expression for the ng-hide directive
* `element_name` If this exists this is an Angular expression that is set to the 'name' attribute of the html element
* `style` The form style to render this widget with. Possible values are `['horizontal', 'vertical']`. Defaults to 'horizontal'
* `rows` The number of rows in the textarea. Used to fill the html textarea row attribute. Defaults to 5.


#### Inference from subrecord fields

A very common pattern is to render form fields that relate to fields of `Subrecords`. Template tags will use this to infer useful information. The display name will be set to the verbose_name and the the ng-model will be inferred.

If its required, it will set as a required field. If its a CharField with a max length it will set a validation rule accordingly.

If the field is a free text or foreign key we will infer the lookup list.

Alternatively if the field has choices attached to it we will infer the choices into the field.

```html
{% input field="Allergies.drug" %}
```

Note unlike the traditional choices implementation only the last value of the choices is used and saved to the database

```python
  Colours = (
    ('P', 'Purple'),
    ('R', 'Red'),
  )
```

What is displayed to the user and saved to the database is 'Purple' or 'Red' respectively.

All inferences can be overridden by declarations in the template tag. For Example

```html
{% input field="Allergies.drug" label="Something else" %}
```

Will render the input with a different label.


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
