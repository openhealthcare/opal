## opal.core.episodes


## EpisodeCategory

OPAL Episodes have an associated category. These categories are implemented as subclasses
of `opal.core.episodes.EpisodeCategory`. This class is an OPAL [DiscoverableFeature](../guides/discoverable.md)
and thus inherits all of the core Discoverable API.

The category of any episode can be accessed as the `.category` property of any `Episode` instance.

### Properties

#### EpisodeCategory.detail_template

This is the template used within the [Patient Detail View](../guides/patient_detail_views.md) to display
information about episodes of this category.

#### EpisodeCategory.start

Returns the Start date of this episode type.

#### EpisodeCategory.stop

Returns the Stop date of this episode type

## InpatientEpisode

This is the defualt EpisodeCategory imlpementation - applications started with OPAL's scaffolding
scripts will use this as the `OpalApplication.default_episode_category`. It sets the detail template to
`detail/inpatient.html`