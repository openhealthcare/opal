## opal.models.Patient

### methods

#### `Patient.demographics()`

Returns the relevant Demographics instance for the patient.

#### `Patient.create_episode()`

Returns a new `Episode` for this patient.

#### `Patient.get_absolute_url()`

Return the URL for this patient

#### `Patient.to_dict`

Return the dictionary representation of this patient - suitable for serialization.

    patient.to_dict(user)

### `Patient.get_latest_created_or_updated`
Returns when the patient last had a child episode, episode subrecord or patient subrecord updated/created (based on the created/updated timestamp). Can take the argument `include_episodes=False` for the latest time only patient subrecords were created/updated.

#### `Patient.bulk_update`

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

### Manager

The custom manager for Patient has the following methods:

#### Patient.objects.search

A useful utility the patient manager has a search method that
will search on first name last name hospital number. Its splits the string input on space, so if you do "12 Jane", you will get all
Patients who's name, surname or hospital number contains either
12 or Jane, in this example most probably people who's hospital
number contains 12 and who's first name is Jane.
