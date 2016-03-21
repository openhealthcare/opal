## opal.models.Patient

### methods

#### create_episode

Returns a new `Episode` for this patient.

#### to_dict

Return the dictionary representation of this patient - suitable for serialization.

    patient.to_dict(user)


#### bulk_update
pass in a dictionary of subrecords you want to update, pass in an episode if one exists.
This method will create all the subrecords and a new episode if necessary in an atomic
transaction
