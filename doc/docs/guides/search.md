# OPAL Search overview

The OPAL Search backend is switchable using the settings value OPAL_SEARCH_BACKEND.

By default it will do a database query.

The backend takes in a dictionary with the following fields

{
      "queryType": either "Equals" or "Contains",
      "field": the label of the column that will be queried, e.g. Hospital Number,
      "query": the value to be queried, e.g. "1111",
      'combine': whether the query is 'and' or 'or' in conjunction with other dictionaries
      'column': the model to be queried e.g. 'demographics'
}
