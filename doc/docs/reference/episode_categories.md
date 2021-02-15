# opal.core.episodes

## EpisodeCategory

Opal [Episodes](../guides/episodes.md) have an associated category. These categories are
implemented as subclasses of `opal.core.episodes.EpisodeCategory`. This class is an Opal
[DiscoverableFeature](../guides/discoverable.md) and thus inherits all of the core
Discoverable API.

The category of any episode can be accessed as the `.category` property of any `Episode` instance.

An episode category must be initialized with an instance of an episode.

```python
from opal.core.episodes import InpatientEpisode

category = InpatientEpisode(episode)
```

** Properties **

### EpisodeCategory.detail_template

This is the template used within the [Patient Detail View](../guides/patient_detail_views.md)
to display information about episodes of this category.

### EpisodeCategory.stages

A list of strings that are valid values for `Episode.stage` for this category.

** Classmethods **

### EpisodeCategory.episode_visible_to(episode, user)

Predidcate function to determine whether an episode of this category is visible
to a particular user.

The default implementation will return True unless `UserProfile.restricted_only` is set to
True. (In which case this user should not see any elements which are visible 'by default' for
this application.)

```python
InpatientEpisode.episode_visible_to(episode, user)

# -> True
```

** Methods **

### EpisodeCategory.get_stages()

Returns a list of stages for this category as strings.

```python
InpatientEpisode(episode).get_stages()
# -> ['Inpatient', 'Followup', 'Discharged']
```

### EpisodeCategory.has_stage(stage)

Predicate function to determine whether a string is a valid stage for this category.

```python
InpatientEpisode(episode).has_stage('Inpatient')
# -> True
```

### EpisodeCategory.is_active()

Predicate function to determine whether this episode is active.

The default implementation looks to see whether an end date has
been set on the episode.

```python
InpatientEpisode(Episode()).is_active()
# -> True
```

### EpisodeCategory.set_stage(stage, user, data)

Sets the stage on the episode. It gets passed the user, and the
rest of the data that's been used to update the episode.

```python
InpatientEpisode(episode).set_stage('Discharged', user, data_dict)
# -> True
```
