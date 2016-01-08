# OPAL Patient List views

OPAL core provides support for displaying spreadsheet-style lists of patients.

A list is comprised of a set of record types to display, and their ordering.

### Registering a list

Your application can have a file called patient_lists.py. This defines the list views
that the application makes available on the list page.

We need a way to get your list patient based on the page url. Usually this will be via tag
if you inherit from TaggedPatientList you need to define a tag and optionally a subtag.
It should also define a queryset of episodes and a schema attribute. The schema attribute
is the list of columns that will be displayed. The queryset is the episodes rows that
will be displayed.

when navigated to /#/list/[[ tag ]]/[[ sub tag ]] this will look up the tag/subtag and
return serialized episodes defined by the queryset.

You can override get_queryset and have access to the request as self.request, to return
a custom queryset based on GET params/user etc.

If you don't want a url like the above, patient lists are got by calling a classmethod get(\*\*url_kwargs) which returns the class.

e.g. /#/other_list/[[ name ]]

could have a class method of

@classmethod
def get(klass, url_kwargs):
  if url_kwargs["name"] === "Larry":
    return klass


### Template selection

The list view is constructed by rendering a column for each record, in the order
defined in the schema, and a row for each episode in the list.

The template for each cell should live in `./templates/records/*`. In order to
select the appropriate template for a given episode, OPAL looks in the following
locations:

    records/{record_name}.html
    records/{team}/{record_name}.html
    records/{team}/{subteam}/{record_name}.html
