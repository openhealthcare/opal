# Form Helpers

OPAL comes with a selection of templatetags that can help you with the
repetitive task of generating Bootstrap and OPAL compatible markup for
your forms.

### {% checkbox ... %}

Generates a checkbox

Keywords:

* `label` The Label with which to describe this input
* `model` The model which we are editing (This is a string that references an in-scope Angular variable)
* `width` Bootstrap small column width of the checkbox
* `labelwidth` Bootstrap small column width of the label


### {% radio ... %}

Generates an inline radio input

Keywords: 

* `label` The Label with which to describe this input
* `model` The model which we are editing (This is a string that references an in-scope Angular variable)
* `show`  A string that contains an Angular expression for the ng-show directive
* `hide`  A string that contains an Angular expression for the ng-hide directive
* `lookuplist` an Angular expression that evaluates to an array containing the radio values
