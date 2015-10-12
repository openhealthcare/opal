## opal.core.search.queries

This module provides our base classes for query backends as well as helper functions.

#### episodes_for_user

Given an iterable of EPISODES and a USER, return a filtered list of episodes that this user has
the permissions to know about.

    filtered_episodes = episodes_for_user(episodes, user)
