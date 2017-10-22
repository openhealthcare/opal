from opal.core.search.search_rule import SearchRule
from opal.core.subrecords import subrecords


def extract_schema_for_model(model):
    serialised = {
        'name': model.get_api_name(),
        'display_name': model.get_display_name(),
        'fields': model.build_field_schema(),
        'description': model.get_description()
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


def extract_search_schema():
    """
        Creates the search schema, ie a combination of all roles
        and subrecords (that are advanced_searchable)
    """
    custom_rules = [i().to_dict() for i in SearchRule.list()]
    subs = (i for i in subrecords() if i._advanced_searchable)
    schema = [
        extract_schema_for_model(s) for s in subs
    ]
    return sorted(custom_rules + schema, key=lambda x: x["display_name"])


def extract_download_schema_for_model(model):
    """
        similar to extract_search_schema but excludes fields
        that one cannot extract
    """
    serialised = extract_schema_for_model(model)
    field_names = model._get_fieldnames_to_extract()
    serialised["fields"] = [
        i for i in serialised["fields"] if i["name"] in field_names
    ]

    return serialised
