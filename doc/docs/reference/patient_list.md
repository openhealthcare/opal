# opal.core.patient_lists

The `patient_lists` module defines a number of classes for working with lists of patients.

## PatientList

...

### Properties

#### PatientList.display_name

How we want to refer to this list on screen to users.

#### PatientList.comparator_service

A custom comparator service to set sort order within a list. Defaults to None.

## TaggedPatientList

Tagged Patient Lists inherit from Patient Lists - as such they have all of the same methods and properties
of Patient Lists.

## CardPatientList
Change your patientlist template_name to "patient_lists/card_list.html".

This will display the patient list as a series of 'cards', more analagous to a twitter stream than a spreadsheet like the default list.

### Properties

#### TaggedPatientList.tag

The main, or parent tag for this list. Should be lowercase, with no numbers or dashes. Underscores are OK.

#### TaggedPatientList.subtag

The child tag for this list. Should be lowercase, with no numbers or dashes. Underscores are OK.

## TabbedPatientListGroup

Groups of Patient Lists to display as tabs at the top of any list in the group.

### Properties

#### TabbedPatientListGroup.member_lists

A list containing the `PatientList` subclasses in this group.

### Classmethods

#### TabbedPatientListGroup.for_list

Returns the group for a given PatientList. Raises ValueError if not passed a PatientList

#### TabbedPatientListGroup.get_member_lists

A hook for dynamically customising the members of this list group.

Returns an iterable of PatientLists. Defaults to the `.member_lists` property

#### TabbedPatientListGroup.get_member_lists_for_user

Returns an iterable of the visible member lists for a given USER

#### TabbedPatientListGroup.visible_to

Predicate function to determine whether this list is meaningfully visible to this USER
