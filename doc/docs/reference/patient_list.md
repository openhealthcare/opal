## opal.core.patient_lists

The `patient_lists` module defines a number of classes for working with lists of patients.


### class opal.core.patient_lists.PatientList

#### PatientList.allow_add_patient
Whether we should show the add patient button. Defaults to `True`.

#### PatientList.allow_edit_teams
Whether we should allow the user to edit teams. Defaults to `True`.

#### PatientList.comparator_service
A custom comparator service to set sort order within a list. Defaults to None.
Further information on Comparators can be found in the [Opal Guides](../guides/list_views.md#customising-sort-order-of-episodes) section.

#### PatientList.direct_add
Further information is available in the [Guides section](../guides/list_views.md#direct-add).

#### PatientList.display_name
How we want to refer to this list on screen to users.

#### PatientList.order
Passing an integer to `PatientList.order` will allow you to control the order of display of Patient Lists in dropdowns and other views. Further information is available in the [Guides section](../guides/list_views.md#ordering-lists).

#### PatientList.queryset
Further information is available in the [Guides section](../guides/list_views.md#querysets).

#### PatientList.schema
Further information is available in the [Guides section](../guides/list_views.md#schemas).

#### PatientList.slug
Further information is available in the [Guides section](../guides/list_views.md#slug).

#### PatientList.template_name

To override the default Patient List template `opal/templates/patient_list/layouts/spreadsheet_list.html` with a custom template specify the path of the custom template (relative to `/myapp/templates/`) with this property.

```python
# myapp/patient_lists.py

class MyPatientList(PatientList):
    template_name = 'my_layout.html'
```

Will look for a template at `/myapp/templates/my_layout.html`.

Opal includes three patient lists out of the box: `spreadsheet_list.html`, `card_list.html`, and `table_list.html`. See *Built-in PatientList Templates* below for further details.

All these patient list layout templates use Django `{% extends %}` syntax to extend their `base` templates respectively. Each of these `base` templates contains Django `{% block %}`s, so you can override selected parts of the base template by creating a new file in `patient_lists/layouts/` called, for example `spreadsheet_list.html`, and redefining the content of those blocks.

```html
<!-- patient_lists/layouts/spreadsheet_list.html -->
{% extends 'patient_lists/layouts/spreadsheet_list_base.html' %}

{% block content %}
... my new block content ...
{% endblock content %}
```


#### PatientList.visible_to
Further information is available in the [Guides section](../guides/list_views.md#access-control).



### class TaggedPatientList
Tagged Patient Lists inherit from Patient Lists - as such they have all of the same methods and properties of Patient Lists.

### Properties

#### TaggedPatientList.tag
The main, or parent tag for this list. Should be lowercase, with no numbers or dashes. Underscores are OK. Further information is available in the [Guides section](../guides/list_views.md#tagged-patient-lists).

#### TaggedPatientList.subtag
The child tag for this list. Should be lowercase, with no numbers or dashes. Underscores are OK.



### class TabbedPatientListGroup
Groups Patient Lists together, to display as tabs at the top of any list in the group.
![patientlist-tabbed-view](../img/patientlist-tabbed-view.png).

#### TabbedPatientListGroup.default_tab
**Required** property which specifies which of the member `PatientList`s should be shown when the tab is selected. Must be a `PatientList` and must be in `member_lists`.

#### TabbedPatientListGroup.display_name
**Required** property which defines the name to be displayed in the list Switcher to represent the TabbedPatientListGroup

#### TabbedPatientListGroup.for_list
Returns the group for a given PatientList. Raises ValueError if not passed a PatientList.

#### TabbedPatientListGroup.get_member_lists
A hook for dynamically customising the members of this list group. Returns an iterable of PatientLists. Defaults to the `.member_lists` property.

#### TabbedPatientListGroup.get_member_lists_for_user
Returns an iterable of the visible member lists for a given user.

#### TabbedPatientListGroup.member_lists
A list containing the `PatientList` subclasses in this group.

#### TabbedPatientListGroup.visible_to
Predicate function to determine whether this list is meaningfully visible to this user.

## Built-in PatientList Templates

Opal includes three patient lists out of the box: `spreadsheet_list.html`, `card_list.html`, and `table_list.html`. 

All these patient list layout templates use Django `{% extends %}` syntax to extend their `base` templates respectively. Each of these `base` templates contains Django `{% block %}`s, so you can override selected parts of the base template by creating a new file in `patient_lists/layouts/` called, for example `spreadsheet_list.html`, and redefining the content of those blocks.

### 'Spreadsheet' PatientList layout

This is the default template, which gives you a 'spreadsheet'-like view of the patient list, with a sidebar containing default demographic info, tags and action tools.

![patientlist-spreadsheet-template](../img/patientlist-spreadsheet-template.png)

### 'Card' PatientList layout

This will display the patient list as a series of 'cards', more analogous to a Twitter stream than the spreadsheet-like appearance of the default list.

![patientlist-card-template](../img/patientlist-card-template.png)

To use this layout, change your PatientList `template_name` to "patient_lists/layouts/card_list.html".

### 'Table' PatientList Layout

This will display the patient list as a wide 'table', similar to the spreadsheet-like appearance of the default list, but without the sidebar and without the ability to edit individual items from this view. This view is commonly used when the user action is to click through to a patient detail view, or to provide action buttons in a column.

![patientlist-table-template](../img/patientlist-table-template.png)

To use, just change your PatientList `template_name` to "patient_lists/layouts/table_list.html".
