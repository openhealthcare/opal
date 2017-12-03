## opal.core.search.queries

This module provides our base classes for query backends as well as helper functions.

#### episodes_for_user

Given an iterable of EPISODES and a USER, return a filtered list of episodes that this user has
the permissions to know about.

    filtered_episodes = episodes_for_user(episodes, user)

#### fuzzy_query

Given a partial fragment for example Jane 123, return all patients that
have either a first name, last name or hospital number including jane or 123.
Under the covers it uses [Patient.objects.search](patient.md#patientobjectssearch). It then
orders patients by which have had their episodes created most recently.
