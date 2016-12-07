# Opal Patient List views

Opal provides support for displaying lists of patients, both via a spreadsheet like view,
and with a card based view.

### Defining lists

Opal patient lists are subclasses of `opal.core.patient_lists.PatientList`.

Typically these are found in a `patient_lists.py` module of your application or plugin. (Lists _can_ be
defined elsewhere, but may not be autodiscovered.)

A basic list needs only define it's `display_name` a `queryset` of episodes to display, and
a `schema` of subrecords to show for each episode.

    # patient_lists.py
    from opal.models import Episore
    from opal.core import patient_lists

    from myapplication import models

    class AlphabetListA(patient_lists.PatientList):
        display_name = 'A Patients'

        queryset = Episode.objects.filter(demographics__name__istartswith='a')

        schema = [
            models.Demographics,
            models.Location,
            models.Diagnosis,
            models.Treatment
        ]

The `display_name` property is the human readable name for our list - which is displayed as
link text to our list.

### Schemas

Schemas are lists of Subrecords that we would like to display in our list. By default we
render the subrecord display_template, and allow editing and addition of each subrecord in
place.


### Template selection


The list view is constructed by rendering a column for each record, in the order
defined in the schema, and a row for each episode in the list.

The template for each cell should live in `./templates/records/*`. In order to
select the appropriate template for a given episode, Opal looks in the following
locations:

    records/{episode_type}/{list slug}/{record_name}.html
    records/{list_slug}/{record_name}.html
    records/{episode_type}/{record_name}.html
    records/{record_name}.html

### Querysets

The queryset property of your list should contain all of the episodes for this particular
list. On occasion we require a more dynamic queryset, in which case we can ovreride the
`get_queryset` method.

    # patient_lists.py
    import datetime
    from opal.models import Episode
    from opal.core import patient_lists

    class MyWeeklyList(patient_lists.PatientList):
        def get_queryset(self):
            one_week_ago = datetime.date.today() - datetime.timedelta(days=1)
            return Episode.objects.filter(date_of_admission__gte=one_week_ago)

### Ordering Lists

As a [discoverable.SortableFeature](discoverable.md) lists may be ordered by setting the
`order` property to an integer. Lists will display in drop-downs, tables et cetera, in
this order.

### Slug

As a [discoverable](discoverable.md) feature, the slug for each list is determined by
either setting the `slug` property, or returning a string from the `get_slug` classmethod.

### Templates

### Tagged Patient Lists

A common model for working with lists is to use lists based on the tags assigned to an episode.
This allows users to add and remove patients from lists as they see fit, rather than attempting
to infer it from other properties of the patient (e.g. their current location for instance.)
which can be particularly challenging for some clinical services.

Opal provides a specific subclass for working with Tagged Patient Lists:

    # patient_lists.py
    from opal.core import patient_lists

    class MyTagList(patient_lists.TaggedPatientList):
        display_name = 'Tagged blue'
        tag = 'blue'

Tagged lists will automatically fetch the appropriate queryset for patients tagged with the tag
you specify.

### Invalid Tagged Patient Lists

Tag names may not have hyphens in them - Opal uses hyphens to distinguish between tags and subtags
in the urls for lists, so attempting to define one will raise an exception.

    class MyList(TaggedPatientList):
        tag = 'foo-bar'

    # This will raise InvalidDiscoverableFeatureError !

### Direct Add

Sometimes, we want to control the flow of patients onto, off, or between lists a little more closely.
For instance, we might need to ensure additional data collection at points in a patient journey.

In order to accomplish this, we often implement custom patient flows that wil programatically tag
episodes to tagged lists. In those cases we will want to prevent users from manually adding or
removing the tags themselves. This can be easily accomplished via the `direct_add` property. When
set to false, users will not be able to add the tag for this list.

    class MyLockedDownList(TaggedPatientList):
        tag = 'liaisonpatients'
        direct_add = False

### Access Control

As PatientLists are a [RestrictableFeature](discoverable.md#restrictable-features), Access control
for lists is set by overriding the `visible_to` classmethod. Your list will only be visible to
those users for whom this method returns `True`.

For instance, we could define a Patient List that was only available to Django Superusers:

    class SuperuserPatientList(PatientList):

        @classmethod
        def visible_to(klass, user):
            return user.is_superuser
