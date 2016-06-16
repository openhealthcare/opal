## OPAL Subrecords

OPAL Subrecords are models that relate to either Patients or Episodes, and inherit from
base classes `opal.models.PatientSubrecord` or `opal.models.EpisodeSubrecord`

### Properties

#### Subrecord._angular_service

Name of the Angular service you would like to use to customise the initialization of this
subrecord in the javascript layer.

```python

class Demographics(PatientSubrecord):
    _angular_service = 'Demographics'
````

#### Subrecord._icon

String that provides the name of the icon to use for forms, column headings etc.

    class Demographics(PatientSubrecord):
        _icon = 'fa fa-user'

#### Subrecord._is_singleton

Boolean that determines whether this subrecord is a singleton.
There may only be one of each singleton Subrecord, which is created whth the parent.

    class Demographics(PatientSubrecord):
        _is_singleton = True

For this case, when a `Patient` is created, an empty `Demographics` instance will
automatically be created.

#### Subrecord._list_limit

Integer to indicate the maximum number of entries to display in list view for this
model. Useful for record types where many entries will accrue, or where display is
particularly verbose.

    class BloodPressureReading(EpisodeSubrecord):
        _list_limit = 3

#### Subrecord._modal

String to indicate a non-default modal size to be used for editing this `Subrecord`.
Valid options are: 'lg', 'sm'. Typically used for complex forms or the display of
additional contextually sensitive information when editing or entering data.

    class Antimicrobial(EpisodeSubrecord):
        _modal = 'lg'

#### Subrecord._sort

Name of the field by which we want to sort these records when displaying.

    class Antimicrobial(EpisodeSubrecord):
        _sort = 'start_date'

#### Subrecord._title

String we would like to use for user-facing display of this record type.

    class Antimicrobial(EpisodeSubrecord):
        _title = 'Abx'


#### Subrecord._clonable

A Boolean that is True by default used by `opal.views.EpisodeCopyToCategoryView`
to determine if instances of this record should be copied across.

    class Antimicrobial(EpisodeSubrecord):
        _clonable = 'False'


#### Subrecord._exclude_from_extract

Boolean to specify that this subrecord should be excluded from any standard data extract.
This implicitly defaults to False.

    class Antimicrobial(EpisodeSubrecord):
        _exclude_from_extract = 'Abx'

#### Subrecord.pid_fields

An iterable of strings that correspond to fieldnames that contain Patient Identifiable Data (PID).

This is used when creating data extracts to exclude PID from e.g. CSV downloads.

### Methods

#### Subrecord.get_display_template()

Classmethod to locate the active display template for our record.

Returns the name of the template or None.

Keywords:

* `episode_type` Optional episode type string to check for form customisations
* `patient_list` Optional patient list slug string to check for form customisations

#### Subrecord.get_form_template()

Classmethod to locate the active template for our record. Returns the name of a template or None.

Keywords:

* `episode_type` Optional episode type string to check for form customisations
* `patient_list` Optional patient list slug string to check for form customisations

#### Subrecord.get_modal_template()

Classmethod to locate the active template for our record. Returns the name of a template or None.

Keywords:

* `episode_type` Optional episode type string to check for modal customisations
* `patient_list` Optional patient list slug string to check for modal customisations


#### Subrecord.get_modal_footer_template

Classmethod to add a custom footer to a modal, used for example to denote if
the data from a model has been sourced from an external source

#### Subrecord.update_from_dict()
An instance method that will update a model with a dictionary. This method is used
to provides a hook for changing the way a subrecord handles being updated from serialised
data.

For example on a new allergy
    allergy.update_from_dict({"drug": "penicillin"})

will update the allergy to have the correct drug

#### Subrecord.bulk_update_from_dicts()

A Classmethod to allow the creation of multiple objects.

Takes in the parent model - an episode
for EpisodeSubrecords a patient for PatientSubrecords. Under the covers it iterates
over all the subrecords, adds in the parent relationship and calls update_from_dict

### Subrecord Mixins

#### TrackedModel

A Tracked Model automatically has created, created_by, updated, updated_by and
these are only updated when used via the api

#### ExternallySourcedModel

Often we want data to be sourced from external systems, this mixin adds in the
fields external_system and external_identifier to allow us to track where
they come from and how they are referenced by that system.

These fields are then often used in forms to make the data read only
