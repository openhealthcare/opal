## Opal mixins

### Serialisable
Provides the information the display name, icon, api name of the model, along with the fields that should be serialised with the model and their titles (verbose_names) and data types (e.g. date, string).


#### build_schema_for_field_name
Takes in a field name and returns a json description of the field.

#### get_human_readable_type

Provides a human readable description of the field name for example
Date & Time for a DateTime Field.

#### get_lookup_list_api_name

Provides the api name of the lookup list related to the field if it exists

#### get_description

Returns model._description, which should be a human readable description of the
model

### ToDictMixin
Provides a method that serialises a model
to a dictionary for example
if we have an allergy model with a field drug
it might serialise like below

    allergy.to_dict() -> {"id": 1, "drug": "penicillin"}


### UpdateFromDict
Provides a method that updates a model
based on a dictionary of fields, for example

For example on a new allergy

    allergy.update_from_dict({"drug": "penicillin"})

will update the allergy to have the drug penicillin.
