## opal.core.search.extract

This module provides our base classes for downloading csv data from opal.


#### generate_multi_csv_extract
Generates a zip directory of a .csv file for every subrecord and every episode.

#### generate_nested_csv_extract
Takes in a field_dict of serializer slug -> \[field names\] on the serializer

Generates a zip directory with an html file with a description of all the fields and a single csv file that has the fields above.

#### Overriding extracts
Extracts are generated from serialisers which are looked up by the api name of the model (either an episode or a subrecord)

One can override the serialisers by using the discoverable serialiser.

In a file called extract.py declare a subclass to opal.core.search.extract.ExtractCsvSerialiser.

Declare it with a slug of either 'episode' or the api name of the subrecord
that you want to override.

##### opal.core.search.extract.ExtractCsvSerialiser.get_schema
takes in the 'model', returns the extract schema, ie what appears in the datadictionay
and what is selectable when the user is decided which fields they would like.

##### opal.core.search.get_row
returns the row that will be outputed
