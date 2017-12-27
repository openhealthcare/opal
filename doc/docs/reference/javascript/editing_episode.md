## The Editing Episode service

The `EditingEpisode` service in `opal.services` provides us with core functionality related
to interacting with episodes forms.

### Constructor

The EditingEpisode can, optionally, be instantiated with an Episode.
The constructor hoists onto itself all the subrecords in a similar
pattern, to the [Episode](episode_service.md).

### Helper

The EditingEpisode has a helper that has the following methods

#### Helper.addRecord('subrecord api name')
Adds a subrecord to the attatched editing object


#### Helper.remove('subrecord api name', idx)
Removes a subrecord of idx from the editing object
e.g. `editing.helper.remove('condition', 0)` will
remove the first condition

#### Helper.update(episode)
Replaces what is currently on 'editing', with a
version of episode converted for use in a form.
