## Forms

### Editing Records

The editing of records is a key component of any Opal application. A key pattern is to edit
or create an individual record in a modal containing the form for just that record. Opal provides
the Angular Controller `opal.controllers.EditItemCtrl` for doing just this

### Customising the Angular Controller

Opal uses the `formController` attribute of an `Item` to determine which Angular Controller to use. This
defaults to `opal.controllers.EditItemCtrl`. Individual Subrecords may customise this by implementing an Angualar record Service
and overriding the formController attribute.

```python
# yourapp/models.py
class Diagnosis(models.Diagnosis):
    _angular_service = 'Diagnosis'
```

```js
// yourapp/static/js/diagnosis.js
angular.module('opal.records').factory('Diagnosis', function(){
    return function(record){
        record.formController = 'MyCustomDiagnosisFormController';
        return record;
    }
});

```

Custom form controllers can use the preSave(itemToBeSaved) hook to add their own custom logic before the item is saved

### Form and modal templates

Subrecords have `get_form_template()` and `get_modal_template()` methods, which are used for
figuring out how to render forms for interacting with them. These use the following template
paths based on the context in which they are called:

    # Forms
    forms/{episode_type}/{list slug}/{record_name}_form.html
    forms/{list_slug}/{record_name}_form.html
    forms/{episode_type}/{record_name}_form.html
    forms/{record_name}_form.html

    # Modals
    modals/{episode_type}/{list slug}/{record_name}_modal.html
    modals/{list_slug}/{record_name}_modal.html
    modals/{episode_type}/{record_name}_modal.html
    modals/{record_name}_modal.html


### Autogenerating forms

The `opal` commandline tool has a scaffold command, which will autogenerate missing form templates
for subrecord models. Simply run the following command to generate.

    $ opal scaffold $DJANGO_APP_WHERE_MODELS_LIVE

(Note this will also generate and run migrations for any unmigrated models.xb)

### Client side Validation

Client side validation for forms requires a pattern and a help block && uses ng-pattern, ng-disabled (https://docs.angularjs.org/api/ng/directive/input)

### Helpers

Opal contains a number of helpers for developing forms and input modals.

Many of these are located in the forms template tag library, which is a
Django templatetag library that understands the context of common patterns with
Opal for creating forms and modals.

It provides helpers for various input types that will allow you to render consistent
forms, with less verbose templates.

    {% load forms %}
    <form class="form-horizontal">
      {% input "autofocus" label="Destination" model="editing.destination" lookuplist="destination_list" %}
      {% datepicker label="Date" model="editing.date" %}
      {% checkbox label="Alone?" model="editing.alone" %}
    </form>


For full documentation of the options, please see the [Form templatetags reference material](/reference/form_templatetags/)
