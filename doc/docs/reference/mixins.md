## OPAL mixins

### SerialisableFields
provides the fields that a model uses for the
fields below for example
if we have an allergy model with a field drug
it might serialise like below

    Allergy._get_fieldnames_to_serialize() -> ["id", "drug"]


### ToDictMixin
provides a method that serialises a model
to a dictionary based on its fields for example
if we have an allergy model with a field drug
it might serialise like below

    allergy.to_dict() -> {"id": 1, "drug": "penicillin"}

### UpdateFromDict
provides a method that updates a model
based on a dictionary of fields, for example

For example on a new allergy

    allergy.update_from_dict({"drug": "penicillin"})

will update the allergy to have the drug penicillin
