## opal.core.search.extract

This module provides our base classes for downloading csv data from opal.

One can override serialisers by subclassing the discoverable
opal.core.search.extract.ExtractCsvSerialiser and giving it the api name
of a subrecord or 'episode'




#### generate_multi_csv_extract
Generates a zip directory of a .csv file for every subrecord and every episode.

#### generate_nested_csv_extract
Takes in a field_dict of serializer slug -> field names on the serializer

Generates a zip directory with an html file with a description of all the fields and a single csv file

 extract types

There are 2 different types of extract, a nested extract and

Given an iterable of EPISODES and a USER, return a filtered list of episodes that this user has
the permissions to know about.

    filtered_episodes = episodes_for_user(episodes, user)

#### fuzzy_query

Given a partial fragment for example Jane 123, return all patients that
have either a first name, last name or hospital number including jane or
