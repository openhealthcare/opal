from opal.core.search.search_rule import SearchRule
from opal.core.subrecords import subrecords
from opal.models import Episode


def serialize_model(model):
    col = {
        'name'        : model.get_api_name(),
        'display_name': model.get_display_name(),
        'fields'      : model.build_field_schema(),
    }

    if hasattr(model, 'get_icon'):
        col["icon"] = model.get_icon()
    for field in col["fields"]:
        field["type_display_name"] = model.get_human_readable_type(
            field["name"]
        )

    col["fields"] = sorted(col["fields"], key=lambda x: x["title"])
    return col


def serialize_schema(schema):
    return [serialize_model(column) for column in schema]


def extract_schema():
    custom_rules = [i().to_dict() for i in SearchRule.list()]
    schema = serialize_schema([
        s for s in subrecords() if s._advanced_searchable
    ])

    return sorted(custom_rules + schema, key=lambda x: x["display_name"])


def data_dictionary_schema():
    schema = []
    to_serialise = list(subrecords())
    to_serialise.append(Episode)

    for subrecord in to_serialise:
        serialised = serialize_model(subrecord)
        extract_fields = subrecord._get_fieldnames_to_extract()

        new_fields = []
        for field in serialised['fields']:
            if field["name"] in extract_fields:
                field["type_display_name"] = subrecord.get_human_readable_type(
                    field["name"]
                )
                new_fields.append(field)
        serialised['fields'] = new_fields

        schema.append(serialised)

    return sorted(schema, key=lambda t: t["display_name"])
