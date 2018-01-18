# opal.models.Episode

The `opal.models.Episode` class represents an episode of care for a patient.
This can be either an inpatient stay, an outpatient treatment, a telephone
liaison, an appointment at a clinic, or any other arbitrarily defined period of care.

## Fields

### Episode.category

The [category](episode_categories) of this episode - e.g. inpatient, outpatient et cetera.
This defaults to whatever is set on your application's subclass of
`opal.core.application.OpalApplication` - which itself defaults to 'inpatient'.

### Episode.patient

A foreign key relationship to the patient for whom this episode concerns.

### Episode.active

A boolean to provide a quick lookup for whether this is an active or closed episode.

### Episode.start

This should be the start of the episode. If this is an inpatient episode, the date of admission.

### Episode.end

This should be the end of the episode. If this is an inpatient episode, the date of discharge.

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

* `shallow` Boolean to indicate whether we want just this episode, or also a sorted set of
previous and subsequent episodes

### Episode.get_tag_names(user)


Arguments:

* `user` The user for whom we want the tag names.

Return the current active tag names for this Episode as strings.

    episode.get_tag_names(user)
    # ['mine', 'infectioncontrol']


### Episode.set_tag_names(tag_names, user)


Arguments:

* `tag_names` The list of tags that we want to be active for this Episode.
* `user` The user for whom we want the tag names.

Set tags for this Episode.

```python
episode.set_tag_names(['mine', 'infectioncontrol'], user)
```

### Episode.set_tag_names_from_tagging_dict(tagging_dict, user)

Arguments:


* `tagging_dict` The dictionary of {tag_name: boolean} tags to set
* `user` The user for whom we want the tag names.

Set tags for this Episode.

```python
episode.set_tag_names_from_tagging_dict({'inpatient': True}, user)
```

### Episode.set_stage(stage, user, data)

Setter function for episode stage. Will validate that the stage given is
valid for the current `EpisodeCategory` and raise `ValueError` if it is invalid.

```python
episode.set_stage('Discharged', user, {})
episode.stage
# -> 'Discharged'
```

## Manager

The custom manager for Episodes has the following methods:


### Episode.objects.serialised()

Return a set of serialised episodes.

    Episode.objects.serialised(User, [episode, ...], historic_tags=False)

Arguments:

* `user` The User for whom we want to serialise this episode
* `episodes` An iterable of Episode instances

Keywords:

* `historic_tags` A boolean to indicate whether the user desires historic or just current tags to
be serialised

### Episode.objects.search

As a useful utility, the episode manager has a search method that will search on first name, last name and/or hospital number, under the hood it uses [Patient search](patient.md#patientobjectssearch)


## opal.core.api.EpisodeViewSet

Gives you an api for create/update/list/retrieve apis for episodes. Its recommended that you use [opal.core.patient_lists](patient_list.md) rather than the list api, as this gives you more flexibility.

The Create api accepts {
    demographics: {{ a serialised demographics model }},
    location: {{ a serialised location model }}.
    tagging: {{ a dictionary of tag names to True }}
}
