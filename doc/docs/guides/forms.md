## Forms

### Editing Records

The editing of records is a key component of any OPAL application. A key pattern is to edit
or create an individual record in a modal containing the form for just that record. OPAL provides
the Angular Controller `opal.controllers.EditItemCtrl` for doing just this

### Modal template selection

Modal templates live in `./templates/modals/*`. For the Demographics subrecord we would
look in `./templates/modals/demographics_modal.html` - which is also available from the URL
`/templates/modals/demographics_modal.html`. Modal or form templates can be customised per
team or sub-team, with template selection handled by the `.get_form_template` classmethod of your
Subrecord.

Team customised subrecords are retrieved from the url e.g.
`/templates/modals/demographics_modal.html/team/subteam/` and will look for templates in 
`./templates/modals/team/subteam/demographics_modal.html`

### Client side Validation

Client side validation for forms requires a pattern and a help block && uses ng-pattern, ng-disabled (https://docs.angularjs.org/api/ng/directive/input)

### Helpers

OPAL contains a number of helpers for developing forms and input modals.

Many of these are located in the forms template tag library, which is a
Django templatetag library that understands the context of common patterns with
OPAL for creating forms and modals. 

It provides helpers for various input types that will allow you to render consistent
forms, with less verbose templates.

    {% load forms %}
    <form class="form-horizontal">
      {% input "autofocus" label="Destination" model="editing.destination" lookuplist="destination_list" %}
      {% datepicker label="Date" model="editing.date" %}
      {% checkbox label="Alone?" model="editing.alone" %}
    </form>


For full documentation of the options, please see the [Form templatetags reference material](/reference/form_templatetags/)
