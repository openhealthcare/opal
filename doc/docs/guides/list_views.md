# OPAL Patient List views

OPAL core provides support for displaying spreadsheet-style lists of patients.

A list is comprised of a set of record types to display, and their ordering.

### Registering a list

Your application will have a `schema_module` defined in its object. This is expected
to be a python module with a `list_schemas` object. The `list_schemas` object should
be a dictionary of team/subteam names that point to lists of models.

If you are using the OPAL scaffolding commands from the command line interface, this
will have been generated for you.

    list_columns = [models.Demographics, models.Diagnosis]
    list_columns_micro = [models.Demographics, models.Diagnosis, models.Antimicrobial]
    list_columns_id_liaison = [models.Demographics, models.Diagnosis, models.Travel]

    list_schemas = {
        'default': list_columns,
        'microbiology': {
            'default': list_columns_micro,
        },
        'infectious_diseases': {
            'id_liaison': list_columns_id_liaison
        }
    }
  
### Registering a list via a plugin

Plugins may register their own schemas by returning dictionaries of similar structure
to the above from the `OpalPlugin.list_schemas()` [method](plugins.md).

### Template selection

The list view is constructed by rendering a column for each record, in the order 
defined in the schema, and a row for each episode in the list.

The template for each cell should live in `./templates/records/*`. In order to 
select the appropriate template for a given episode, OPAL looks in the following
locations:

    records/{record_name}.html
    records/{team}/{record_name}.html
    records/{team}/{subteam}/{record_name}.html
