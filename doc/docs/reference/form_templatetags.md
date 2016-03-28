# Form Helpers

OPAL comes with a selection of templatetags that can help you with the
repetitive task of generating Bootstrap and OPAL compatible markup for
your forms.


### {% checkbox ... %}

Generates a checkbox

Keywords:

* `field` a string of the models api name '.' field from this it calculates the label, model and will infer the lookuplist if required
* `label` The Label with which to describe this field
* `model` The model which we are editing (This is a string that references an in-scope Angular variable)
* `disabled` If this exists, we use this as the expression for the ng-disabled directive

### {% datepicker ... %}

Generates a datepicker

Keywords:

* `field` a string of the models api name '.' field from this it calculates the label, model and will infer the lookuplist if required
* `label` The Label with which to describe this field
* `model` The model which we are editing (This is a string that references an in-scope Angular variable)
* `show`  A string that contains an Angular expression for the ng-show directive
* `hide`  A string that contains an Angular expression for the ng-hide directive
* `required` Label to show when we're required
* `mindate` Expression to use to set the minimum possible date

### {% input ... %}

Generates an Input

Keywords:

* `field` a string of the models api name '.' field from this it calculates the label, model and will infer the lookuplist if required
* `label` The Label with which to describe this field
* `model` The model which we are editing (This is a string that references an in-scope Angular variable)
* `show`  A string that contains an Angular expression for the ng-show directive
* `hide`  A string that contains an Angular expression for the ng-hide directive
* `lookuplist` an Angular expression that evaluates to an array containing the lookuplist values
* `required` Label to show when we're required
* `enter` expression to evaluate if the user presses return when in this input
* `maxlength` maximum number of characters for this input. Will render the form invalid and display help text if exceeded.

### {% radio ... %}

Generates an inline radio input

Keywords:

* `field` a string of the models api name '.' field from this it calculates the label, model and will infer the lookuplist if required
* `label` The Label with which to describe this input
* `model` The model which we are editing (This is a string that references an in-scope Angular variable)
* `show`  A string that contains an Angular expression for the ng-show directive
* `hide`  A string that contains an Angular expression for the ng-hide directive
* `lookuplist` an Angular expression that evaluates to an array containing the radio values

### {% select ... %}

Generates an inline select input

Keywords:

* `field` a string of the models api name '.' field from this it calculates the label, model and will infer the lookuplist if required
* `label` The Label with which to describe this input
* `model` The model which we are editing (This is a string that references an in-scope Angular variable)
* `show`  A string that contains an Angular expression for the ng-show directive
* `hide`  A string that contains an Angular expression for the ng-hide directive
* `lookuplist` an Angular expression that evaluates to an array containing the radio values
* `other` A boolean parameter that if true, provides a free text option when 'Other' is selected
* `help` a template to use as the contents of a help popover

### {% textarea ... %}

Generates an inline textarea input

Keywords:

* `field` a string of the models api name '.' field from this it calculates the label, model and will infer the lookuplist if required
* `label` The Label with which to describe this input
* `model` The model which we are editing (This is a string that references an in-scope Angular variable)
* `show`  A string that contains an Angular expression for the ng-show directive
* `hide`  A string that contains an Angular expression for the ng-hide directive


### {% icon "icon-name" %}

Renders a Bootstrap style Icon tag.
If the icon starts with `fa` or `glyphicon` then we will insert the preceding `fa`.

    {% icon "fa-user-md" %}
    <i class="fa fa-user-md"></i>

    {% icon "cusom-icon"}
    <i class="custom-icon"></i>
