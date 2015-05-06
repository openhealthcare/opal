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

## Methods

The Episode model has the following methods: 

### Episode.to_dict

Return a dictionary of field value pairs for this episode

    episode.to_dict(user)

Arguments: 

* `user` The User for whom we want to serialise this episode

Keywords: 

* `shallow` Boolean to indicate whether we want just this episode, or also a sorted set of previous and subsequent episodes

## Manager

The custom manager for Episodes has the following methods:

### Episode.objects.serialised()

Return a set of serialised episodes.

    Episode.objects.serialised(User, [episode, ...], historic_tags=False)

Arguments:

* `user` The User for whom we want to serialise this episode
* `episodes` An iterable of Episode instances

Keywords: 

* `historic_tags` A boolean to indicate whether the user desires historic or just current tags to be serialised
