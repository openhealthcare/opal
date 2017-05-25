# Opal Search overview

The Opal Search backend is switchable using the settings value Opal_SEARCH_BACKEND.

By default it will do a database query.

The backend takes in a dictionary with the following fields

{
      "queryType": either "Equals" or "Contains",
      "field": the label of the column that will be queried, e.g. Hospital Number,
      "query": the value to be queried, e.g. "1111",
      'combine': whether the query is 'and' or 'or' in conjunction with other dictionaries
      'column': the model to be queried e.g. 'demographics'
}


### The Advanced search interface

The Opal advanced search interface at `/#/extract` allows users to specify rules by which to query for episodes.

By default this allows users to construct simple logical queries based on the values of any subrecord field.

The interface respects the types of fields - for instance using before/after for date fields or equals/contains
for text fields.

This screen also allows users to download episode data for the cohort that matches the specified rules.

### Custom Search Rules

These rules are extensible, allowing custom rules that perform more advanced queries to be inserted.

#### opal.core.search.SearchRule

Is a [discoverable](../guides/discoverable.md).

It is defined with a group of SearchRuleFields that appear like subrecord model fields in the
front end.

The SearchRuleField has a query method that returns a list of Episodes.

The SearchRuleField must define a field_type, these then provide the following operators
to the front end

|  field_type | queryType   |
|---|---|
|  string | equals, contains  |
|  date_time | before, after  |
|  date | before, after  |

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
