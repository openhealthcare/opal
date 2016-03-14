# opal.core.patient_lists

The `patient_lists` module defines a number of classes for working with lists of patients.

## PatientList

...

### Properties

#### PatientList.display_name

How we want to refer to this list on screen to users.

## TaggedPatientList

Tagged Patient Lists inherit from Patient Lists - as such they have all of the same methods and properties
of Patient Lists.

### Properties

#### TaggedPatientList.tag

The main, or parent tag for this list. Should be lowercase, with no numbers or dashes. Underscores are OK.

#### TaggedPatientList.subtag

The child tag for this list. Should be lowercase, with no numbers or dashes. Underscores are OK.
