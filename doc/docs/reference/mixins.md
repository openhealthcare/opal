## Opal mixins

### SerialisableFields
provides the fields that are on the model for example
if we have an allergy model with a field drug
it might serialise like below

    Allergy._get_fieldnames_to_serialize() -> ["id", "drug"]

if you don't want your subrecord serialised as part of the record api
or extract schema api (what is used by advanced search), set _serialisable=False
on your subrecord


### ToDictMixin
provides a method that serialises a model
to a dictionary for example
if we have an allergy model with a field drug
it might serialise like below

    allergy.to_dict() -> {"id": 1, "drug": "penicillin"}

#### ToDictMixin._bulk_serialise

Used by episode and patient. This flag is used to determine whether the item is serialised as part of Episode/Patient.to_dict.


### UpdateFromDict
provides a method that updates a model
based on a dictionary of fields, for example

For example on a new allergy

    allergy.update_from_dict({"drug": "penicillin"})

will update the allergy to have the drug penicillin
