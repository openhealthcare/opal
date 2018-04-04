# Opal Patient List views

Opal provides support for displaying lists of patients, both via a spreadsheet like view,
and with a card based view.

### Defining lists

Opal patient lists are subclasses of `opal.core.patient_lists.PatientList`.

Typically these are found in a `patient_lists.py` module of your application or plugin. (Lists _can_ be
defined elsewhere, but may not be auto discovered.)

A basic list needs only define its `display_name` a `queryset` of episodes to display, and
a `schema` of subrecords to show for each episode.

    # patient_lists.py
    from opal.models import Episode
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

The schema attribute declares the columns of a PatientList. The entries in a schema may either
be `Subrecord` instances, or instances of `opal.core.patient_lists.Column`.

#### Custom Columns

Although most schema entries will be subrecords, it can be useful to have non-subrecord columns.
For instance because you want to allow a composite
column of multiple `Subrecords` or because we want to simply render arbitrary markup.

Columns require the title, and template_path to be set, and are simply included in the schema
list.

```python
class MyMarkupList(patient_lists.PatientList):
    schema = [
        patient_lists.Column(title='Foo', template_path='foo/bar')
    ]

```

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
list. On occasion we require a more dynamic queryset, in which case we can override the
`get_queryset` method.

    # patient_lists.py
    import datetime
    from opal.models import Episode
    from opal.core import patient_lists

    class MyWeeklyList(patient_lists.PatientList):
        def get_queryset(self):
            one_week_ago = datetime.date.today() - datetime.timedelta(days=1)
            return Episode.objects.filter(start__gte=one_week_ago)

### Ordering Lists

As a [discoverable.SortableFeature](discoverable.md) lists may be ordered by setting the
`order` property to an integer. Lists will display in drop-downs, tables et cetera, in
this order.

### Slug

As a [discoverable](discoverable.md) feature, the slug for each list is determined by
either setting the `slug` property, or returning a string from the `get_slug` classmethod.

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

In order to accomplish this, we often implement custom patient flows that will programatically tag
episodes to tagged lists. In those cases we will want to prevent users from manually adding or
removing the tags themselves. This can be easily accomplished via the `direct_add` property. When
set to false, users will not be able to add the tag for this list.

    class MyLockedDownList(TaggedPatientList):
        tag = 'liaisonpatients'
        direct_add = False


### Customising Sort order of Episodes

By default, PatientLists sort according by `start`, then `first_name`, then `surname` using
the Angular method `Episode.compare`. You may override this
on a list-by-list basis by setting the `comparator_service` attribute.

```python
class MySortedList(PatientList):
    comparator_service = 'MyComparatorService'
```

This attribute should be the name of an Angular service that returns a list of comparator functions.
For instance, to sort by Episode.category_name then Episode id:

```javascript
angular.module('opal.services')
    .factory('MyComparatorService', function(){
        "use strict";
        return [
            function(e){ return e.category_name },
            function(e){ return e.id }
        ]
    })
```

<blockquote><small>
The file containing your comparator service must be included in the javascripts <br />
of your application or plugin in order to be available on the client.
</small></blockquote>


### Access Control

As PatientLists are a [RestrictableFeature](discoverable.md#restrictable-features), Access control
for lists is set by overriding the `visible_to` classmethod. Your list will only be visible to
those users for whom this method returns `True`.

For instance, we could define a Patient List that was only available to Django Superusers:

    class SuperuserPatientList(PatientList):

        @classmethod
        def visible_to(klass, user):
            return user.is_superuser

## Grouping related Patient Lists

We commonly require groups of patient lists for a single clinical service. For example a busy
outpatients clinic might have one list of people in the waiting room, one list of people being
triaged, one list for people waiting to see the medical staff, and another for people who have
been seen but need review - for instance because they have outstanding test results.

Opal provides the `TabbedPatientListGroup` class to help with this case. Tabbed Patient List
Groups are an ordered collection of related Patient Lists that are displayed as tabs at the
top of any list in the group.

### Defining a Tabbed Patient List Group

Defining a group can be as simple as declaring member lists in a property.

```python
# yourapp/patient_lists.py

from opal.core import patient_lists

# ... Define your lists here

class MyListGroup(patient_lists.TabbedPatientListGroup):
    member_lists = [MyFirstPatientList, MySecondPatientList, ...]
```


<blockquote><small>
Tabbed Patient List Groups are a Discoverable feature, we expect them to be in a
module named patient_lists.py in one of the Django apps in your application.
</small></blockquote>

### Customising membership

The members of your group can be determined dynamically by overriding the `get_member_lists`
classmethod of your group:

```python
class MyListGroup(patient_lists.TabbedPatientListGroup):
    @classmethod
    def get_member_lists(klass):
        # return an iterable of PatientList subclasses
```

### Restricting access

By default, the UI for a `TabbedPatientListGroup` is shown at the top of any member `PatientList`
as long as there are more than one members of the group visible to the given user.

This behaviour can be customised by overriding the `visible_to` classmethod:

```python
class MyListGroup(patient_lists.TabbedPatientListGroup):
    @classmethod
    def visible_to(klass, user):
        # return True or False appropriately
```

### Customising templates

Applications may customise the UI for Tabbed Patient List Groups by customising the template
`patient_lists/tabbed_list_group.html`.

The default template simply extends `patient_lists/tabbed_list_group_base.html`.
