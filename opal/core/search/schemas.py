from opal.core.search.search_rule import SearchRule
from opal.core.subrecords import subrecords


def serialise_schema(schema):
    return [extract_schema_for_model(column) for column in schema]


def extract_schema():
    custom_rules = [i().to_dict() for i in SearchRule.list()]
    schema = serialise_schema([
        s for s in subrecords() if s._advanced_searchable
    ])
    return sorted(custom_rules + schema, key=lambda x: x["display_name"])


def extract_schema_for_model(model):
    serialised = {
        'name'        : model.get_api_name(),
        'display_name': model.get_display_name(),
        'fields'      : model.build_field_schema(),
    }

    if hasattr(model, 'get_icon'):
        serialised["icon"] = model.get_icon()
    for field in serialised["fields"]:
        field["type_display_name"] = model.get_human_readable_type(
            field["name"]
        )

    new_fields = []
    for field in serialised['fields']:
        field["type_display_name"] = model.get_human_readable_type(
            field["name"]
        )
        new_fields.append(field)
    serialised['fields'] = new_fields
    serialised["fields"] = sorted(
        serialised["fields"], key=lambda x: x["title"]
    )
    return serialised


def extract_download_schema_for_model(model):
    serialised = extract_schema_for_model(model)
    field_names = model._get_fieldnames_to_extract()
    serialised["fields"] = [
        i for i in serialised["fields"] if i["name"] in field_names
    ]

    return serialised
