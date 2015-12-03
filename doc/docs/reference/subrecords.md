## OPAL Subrecords

OPAL Subrecords are models that relate to either Patients or Episodes, and inherit from
base classes `opal.models.PatientSubrecord` or `opal.models.EpisodeSubrecord`

### Properties

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

#### Subrecord.pid_fields

An iterable of strings that correspond to fieldnames that contain Patient Identifiable Data (PID).

This is used when creating data extracts to exclude PID from e.g. CSV downloads.

### Methods

#### Subrecord.get_display_template()

Classmethod to locate the active display templte for our record.

Returns the name of the template or None.

Keywords:

* `team` Optional team to check for form customisations
* `subteam` Optional subteam to check for form customisations


#### Subrecord.get_modal_template()

Classmethod to locate the active template for our record. Returns the name of a template or None.

Keywords: 

* `team` Optional team to check for form customisations
* `subteam` Optional subteam to check for form customisations
