## Forms

### Client side Validation

Client side validation for forms requires a pattern and a help block && uses ng-pattern, ng-disabled (https://docs.angularjs.org/api/ng/directive/input)

### Helpers

OPAL contains a number of helpers for developing forms and input modals.

Many of these are located in the forms template tag library, which is a
Django templatetag library that understands the context of common patterns with
OPAL for creating forms and modals. 

It provides helpers for various input types that will allow you to render consistent
forms, with less verbose templates.

For full documentation of the options, please see opal/templatetags/forms.py
For example usage please see elcid/elcid/templates/*_modal.html
