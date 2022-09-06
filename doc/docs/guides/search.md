# Opal Search overview

The Opal Search backend is switchable using the settings value OPAL_SEARCH_BACKEND.

By default it will do a database query.

The backend takes in a dictionary with the following fields

```
{
      "queryType": either "Equals" or "Contains",
      "field": the label of the column that will be queried, e.g. Hospital Number,
      "query": the value to be queried, e.g. "1111",
      'combine': whether the query is 'and' or 'or' in conjunction with other dictionaries
      'column': the model to be queried e.g. 'demographics'
}
```

## Customisation of search results

Search results are rendered with the template `partials/_patient_summary_list.html`. To
improve performance of serializing multiple patients, the backend returns a patient summary
for the current page of search results.

To add data to these results the application can implement a `PatientSummary` class.

The following example adds the title to the data returned to the front end.

```
from opal.core.search.queries import PatientSummary

class MyPatientSummary(PatientSummary):
    def __init__(self, patient, episodes):
        super()__init__(patient, episodes)
        self.patient_title = patient.demographics().title

    def to_json(self):
        as_json = super().to_json()
        as_json['title'] = self.patient_title
        return as_json


class MyCustomBackend(DatabaseQueryBackend):
    patient_summary_class = PatientSummary

# change settings.py to include OPAL_SEARCH_BACKEND='{path to my backend}.MyCustomBackend'
```

The raw serialised data is available to the front end in a `.data` property.

```
[[ result.data.title ]] [[ result.first_name ]] [[ result.surname ]] [[ result.hospitalNumber ]]
```

## The Advanced search interface

The Opal advanced search interface at `/#/extract` allows users to specify rules
by which to query for episodes.

By default this allows users to construct simple logical queries based on the
values of any subrecord field.

The interface respects the types of fields - for instance using before/after for
date fields or equals/contains for text fields.

This screen also allows users to download episode data for the cohort that matches
the specified rules.

## Custom Search Rules

These rules are extensible, allowing custom rules that perform more advanced
queries to be inserted.

### opal.core.search.SearchRule

Is a [discoverable](../guides/discoverable.md).

It is defined with a group of SearchRuleFields that appear like subrecord model
fields in the front end.

The SearchRuleField has a query method that returns a list of Episodes.

The SearchRuleField must define a field_type, these then provide the following
operators to the front end

|  field_type | queryType   |
|---|---|
|  string | equals, contains  |
|  date_time | before, after  |
|  date | before, after  |
|  boolean | true, false  |
|  null_boolean | true, false  |
|  many_to_many | a list of the lookup list for this field  |
|  many_to_many_multi_select | a multi select field, defined by the enum field from the rule  |

ie if you state the field is a string, the user will be provided with an
equals/contains, which will be passed to the query as given_query["queryType"]



For example

```python
class SomeField(SearchRuleField):
    display_name = "Some Field" # the display name of the field
    description = "A Description for the user to explain what this field means"
    field_type = "date_time" # what kind of filter that is offered, datetime will off before and after

    def query(self, given_query):
        return Episode.objects.all()


class MyCustomQuery(SearchRule):
    display_name = "My Custom Query"
    fields = (SomeField,)
```

## Autocomplete search

Opal contains autocomplete search functionality for the navbar search box.

You can enable it with the setting `OPAL_AUTOCOMPLETE_SEARCH` (defaults to False).

```python
# yourapp/settings.py
OPAL_AUTOCOMPLETE_SEARCH = True
```
