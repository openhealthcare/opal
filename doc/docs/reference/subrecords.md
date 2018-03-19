## Opal Subrecords

Opal Subrecords are models that relate to either Patients or Episodes, and inherit from
base classes `opal.models.PatientSubrecord` or `opal.models.EpisodeSubrecord`

They themselves inherit from the mixins `opal.models.ToDictMixin`, `opal.models.UpdateFromDict`

### Properties

#### Subrecord._angular_service

Name of the Angular service you would like to use to customise the initialization of this
subrecord in the javascript layer.

```python

class Demographics(PatientSubrecord):
    _angular_service = 'Demographics'
```

#### Subrecord._icon

String that provides the name of the icon to use for forms, column headings etc.

    class Demographics(PatientSubrecord):
        _icon = 'fa fa-user'

#### Subrecord._is_singleton

Boolean that determines whether this subrecord is a singleton.
There may only be one of each singleton Subrecord, which is created with the parent.

```python
    class Demographics(PatientSubrecord):
        _is_singleton = True
```

For this case, when a `Patient` is created, an empty `Demographics` instance will
automatically be created.

#### Subrecord._list_limit

Integer to indicate the maximum number of entries to display in list view for this
model. Useful for record types where many entries will accrue, or where display is
particularly verbose.

```python
    class BloodPressureReading(EpisodeSubrecord):
        _list_limit = 3
```

#### Subrecord._sort

Name of the field by which we want to sort these records when displaying.

```python
    class Antimicrobial(EpisodeSubrecord):
        _sort = 'start_date'
```

#### Subrecord._title

String we would like to use for user-facing display of this record type.

```python
    class Antimicrobial(EpisodeSubrecord):
        _title = 'Abx'
```

#### Subrecord._clonable

A Boolean that is True by default used by `opal.views.EpisodeCopyToCategoryView`
to determine if instances of this record should be copied across.

```python
    class Antimicrobial(EpisodeSubrecord):
        _clonable = 'False'
```

#### Subrecord._exclude_from_extract

Boolean to specify that this subrecord should be excluded from any standard data extract.
This implicitly defaults to False.

```python
    class Antimicrobial(EpisodeSubrecord):
        _exclude_from_extract = 'Abx'
```

#### Subrecord.pid_fields

An iterable of strings that correspond to fieldnames that contain Patient Identifiable Data (PID).

This is used when creating data extracts to exclude PID from e.g. CSV downloads.

### Methods

#### Subrecord.get_api_name()

Classmethod that returns a snake case version of the API name for this subrecord.
This will be used in the URL for the subrecord API, and as a property name in Javascript
representations of the data.

```python
>>> Demographics.get_api_name()
"demographics"
```

#### Subrecord.get_display_template()

Classmethod to locate the display template for our record. By default this
looks in the location `{{ template_dir }}/records/{{ subrecord api name }}.html`.

Keywords:

* `prefixes` An optional list of prefixes that allow you to put templates behind an optional
directory for example:

```python
  Subrecord.get_display_template(prefixes=["example"])
```

Would use the first template it found, looking at:

```
{{ template_dir }}/records/example/subrecord.html
{{ template_dir }}/records/subrecord.html
```

#### Subrecord.get_detail_template()

Classmethod to locate a more detailed template for the subrecord. This is the
template used by the record panel. It looks for a template in
`{{ template_dir }}/records/{{ subrecord api name }}_detail.html`.

It defaults to the display template if it can't find one there.


Keywords:

* `prefixes` An optional list of prefixes that allow you to put templates behind an optional
directory for example:

```python
  Subrecord.get_display_template(prefixes=["example"])
```

Would use the first template it found, looking at:
```
{{ template_dir }}/records/example/subrecord_detail.html
{{ template_dir }}/records/example/subrecord.html
{{ template_dir }}/records/subrecord_detail.html
{{ template_dir }}/records/subrecord.html
```


#### Subrecord.get_form_template()

Classmethod to locate the active template for our record. Returns the name of a template or None.
It looks for a template in `{{ template_dir }}/forms/{{ subrecord api name }}_form.html`

Keywords:

* `prefixes` An optional list of prefixes that allow you to put templates behind an optional
directory for example:

```python
  Subrecord.get_form_template(prefixes=["example"])
```

Would use the first template it found, looking at:
```
{{ template_dir }}/forms/example/subrecord_form.html
{{ template_dir }}/forms/subrecord_form.html
```


#### Subrecord.get_modal_template()

Classmethod to locate the active template for our record. Returns the name of a template or None.
By default it will render a modal with a form template from Subrecord.get_form_template(). You can
override this by putting a template named `{{ template_dir }}/modals/{{ subrecord api name }}_modal.html`

Keywords:

* `prefixes` An optional list of prefixes that allow you to put templates behind an optional
directory for example:

```python
  Subrecord.get_modal_template(prefixes=["example"])
```

Would use the first template it found, looking at:
```
{{ template_dir }}/modals/example/subrecord_modal.html
{{ template_dir }}/modals/subrecord_modal.html
```

And default to a modal containing the [Subrecord.get_form_template](#subrecordget_form_template).


#### Subrecord.get_modal_footer_template

Classmethod to add a custom footer to a modal, used for example to denote if
the data from a model has been sourced from an external source


#### Subrecord.bulk_update_from_dicts()

A Classmethod to allow the creation of multiple objects.

Takes in the parent model - an episode
for EpisodeSubrecords a patient for PatientSubrecords. Under the covers it iterates
over all the subrecords, adds in the parent relationship and calls update_from_dict. It returns a list of the objects updated.

### Subrecord Mixins

#### TrackedModel

A Tracked Model automatically has created, created_by, updated, updated_by and
these are only updated when used via the api

#### ExternallySourcedModel

Often we want data to be sourced from external systems, this mixin adds in the
fields external_system and external_identifier to allow us to track where
they come from and how they are referenced by that system.

These fields are then often used in forms to make the data read only
