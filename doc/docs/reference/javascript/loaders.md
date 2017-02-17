## The Patient List Loader service

The `patientListLoader` service in `opal.services` provides a function that will get the episodes from a
previously defined [patient list](patient_list.md)

By default this will be the tag in the route params, alternatively you can pass in a tag.

## The Episode Loader service

Loads in an episode from an id, either passed in, or as the parameter of 'id' on the current route. It casts it to an [Episode](episode_service.md)
