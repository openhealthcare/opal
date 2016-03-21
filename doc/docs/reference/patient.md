## opal.models.Patient

### methods

#### create_episode

Returns a new `Episode` for this patient.

#### to_dict

Return the dictionary representation of this patient - suitable for serialization.

    patient.to_dict(user)


#### bulk_update

Create or update many subrecords in one go, from a serialised dictionary of data.

Pass in a dictionary of subrecords you want to update, as well as an episode if one exists.
This method will create all the subrecords and implicitly create a new episode if required.

This API will execute all create/update operations as an atomic transaction.

For example the following will create a patient:

    patient = Patient()
    patient.bulk_update(
      {
        "demographics": "hospital_number": "1231212",
        "allergies": [
            {"drug": "penicillin"},
            {"drug": "aspirin"},
        ]
      },
      user
    )
