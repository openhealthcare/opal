The `opal.models.Episode` class represents an episode of care for a patient. This can be either 
an inpatient stay, an outpatient treatment, a telephone liaison, an appointment at a clinic, 
or any other arbitrarially defined period of care.

## Fields

### Episode.category

The category of this episode - e.g. inpatient, outpatient et cetera.
This defaults to whatever is set on your application's subclass of 
`opal.core.application.OpalApplication` - which itseflf defaults to 'inpatient'.

### Episode.patient

A foreign key relationship to the patient for whom this episode concerns.

### Episode.active

A boolean to provide a quick lookup for whether this is an active or closed episode.

### Episode.date_of_admission

If this is an inpatient episode, the date of admission.

### Episode.discharge_date

If this is an inpatient episode, the date of discharge.

### Episode.date_of_episode

If this is an episode that occurs on one date (like a clinic visit or telephone liaison), the 
date of that event.

### Episode.consistency_token 

A (automatically generated) hash of the above fields. This is used for detecting concurrent edits.
