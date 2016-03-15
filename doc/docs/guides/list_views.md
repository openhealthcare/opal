# OPAL Patient List views

OPAL provides support for displaying lists of patients, both via a spreadsheet like view,
and with a card based view.

## Defining lists

OPAL patient lists are subclasses of `opal.core.patient_lists.PatientList`. Typically these
are found in a `patient_lists.py` module of your application or plugin. (Lists _can_ be
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

## Schemas

Schemas are lists of Subrecords that we would like to display in our list. By default we
render the subrecord display_template, and allow editing and addition of each subrecord in
place.

### Template selection


The list view is constructed by rendering a column for each record, in the order
defined in the schema, and a row for each episode in the list.

The template for each cell should live in `./templates/records/*`. In order to
select the appropriate template for a given episode, OPAL looks in the following
locations:

    records/{record_name}.html
    records/{team}/{record_name}.html
    records/{team}/{subteam}/{record_name}.html

## Querysets

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

## Ordering Lists

## Slug

## Templates

## Tagged Patient Lists

A common model for working with lists is to use lists based on the tags assigned to an episode.
This allows users to add and remove patients from lists as they see fit, rather than attempting
to infer it from other properties of the patient (e.g. their current location for instance.)
which can be particularly challenging for some clinical services.

OPAL provides a specific subclass for working with Tagged Patient Lists:

    # patient_lists.py
    from opal.core import patient_lists

    class MyTagList(patient_lists.TaggedPatientList):
        display_name = 'Tagged blue'
        tag = 'blue'

Tagged lists will automatically fetch the appropriate queryset for patients tagged with the tag
you specify.

### Invalid Tagged Patient Lists

Tag names may not have hyphens in them - OPAL uses hyphens to distinguish between tags and subtags
in the urls for lists, so attempting to define one will raise an exception.

    class MyList(TaggedPatientList):
        tag = 'foo-bar'

    # This will raise InvalidDiscoverableFeatureError !

## Access Control
