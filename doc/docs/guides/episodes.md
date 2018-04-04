# Opal Episodes

In Opal a Patient may have one or many Episodes. An Episode contains some metadata
such as a start and end date, and the type of episode. This may be an inpatient
stay, an outpatient treatment, a telephone consultation  - or any other arbitrarily
defined period of care.


## Episode Categories

An episode must have a related category. An Opal `EpisodeCategory` is a discoverable
subclass of `opal.core.episodes.EpisodeCategory` - such as `InpatientEpisode`,
`OutpatientEpisode` or `LiaisonEpisode`.

You can access the current category of an episode via the `category` property, while
it is represented in the database in the field `category_name` which will contain
the `display_name` attribute of the relevant category.

```python
episode = patient.episode_set.first()
print episode.category
# <opal.core.episode.InpatientEpisode object>

print episode.category.display_name
# "Inpatient"

print episode.category_name
# "Inpatient"
```

## Detail templates

The category of an episode determines which template will be used to display it
on the detail page for the patient. This template is determined by looking up
the `detail_template` attribute of the `EpisodeCategory`.

```python
episode.category
print episode.category
# <opal.core.episode.InpatientEpisode object>

print episode.category.detail_template
# detail/inpatient.html
```

## Default Category

The default category of episodes in an Opal application is set by the
[OpalApplication](../reference/opal_application) object's default_episode_category
property.

```python
class Application(application.OpalApplication):
    default_episode_category = MyCategory.display_name
```

## Episode stages

An Episode will frequently consist of a number of possible stages. For instance,
for an inpatient episode, a patient will first be an inpatient, and then an
be discharged, with an optional interim follow up stage for inpatients who have been
discharged but requrie further follow up.

Opal stores the stage of an episode as a string in the `stage` property of an
`Episode`. The valid possible stages for a category are accessed from the
`get_stages` method of the category.

```
episode.category.get_stages()
# ['Inpatient', 'Followup', 'Discharged']

episode.category.has_stage('Followup')
# True
```

## Defining your own EpisodeCategory

As EpisodeCategory is a [discoverable](discoverable) we can define our own to
meet custom requirements.

Episode categories should be defined in a file named `episode_categories` of
your application or plugin.

```python
# yourapp/episode_categories.py

from opal.core import episodes


class DropInClinicEpisode(episodes.EpisodeCategory):
    display_name = "Drop-in clinic"
    detail_template = "detail/drop_in.html"

```
