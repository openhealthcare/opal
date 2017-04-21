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


### Custom Search Rules

The Opal search allows you to write a custom rule, for example if you don't want to query by a subrecord.

#### opal.core.search.SearchRule
Is a [discoverable](../guides/discoverable.md)
