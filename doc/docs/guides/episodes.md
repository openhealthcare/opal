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
# <{{ your app name }}.InpatientEpisode object>

print episode.category.display_name
# "Inpatient"

print episode.category_name
# "Inpatient"
```

## Detail templates

The category of an episode determines which template will be used to display it
on the detail page for the patient. This template is determined by looking up
the `detail_template` attribute of the `EpisodeCategory`.

The Episode Category template does not comprise the entire
[Patient detail view](patient_detail_views.md). This is made of multiple episodes
and by default will display some basic demographic details as well as other episodes.
More detail on customising the rest of the detail tempalte is found in the detail view
[Template selection docs](patient_detail_views.md#template-selection).

## Default Category

The default category of episodes in an Opal application is set by the
[OpalApplication](../reference/opal_application.md) object's default_episode_category
property.

```python
class Application(application.OpalApplication):
    default_episode_category = MyCategory.display_name
```

## Defining your own EpisodeCategory

As EpisodeCategory is a [discoverable](discoverable.md) we can define our own to
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

## Episode.active

The field `.active` is used to distinguish Episodes which are ongoing. This field
is set implicitly by the `Episode.save()` method, and there will generally be no
need to set this field directly as part of application code.

Whether an Episode is considered active is determined by the `.is_active()` method
of the relevant EpisodeCategory.

The default implementation considers any Episode without an `.end` date to be active
and any Episode with one to be inactive.

Applications may customise this behaviour by overriding the `.is_active()` method.

For instance, to create a category which considered any Episode older than 2 weeks to
be inactive, one might override the method as follows:

```python
# yourapp/episode_categories.py
import datetime
from opal.core import episodes


class TwoWeeksAndStopCaringEpisode(episodes.EpisodeCategory):
    def is_active(self):
        delta = datetime.date.today() - self.episode.start
        return bool(delta >= datetime.timedelta(days=14))

```

(Note that this would not alter the value in the database immediately after those 2
weeks, but would alter the value the next time the `Episode.save()` method was called.)

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
