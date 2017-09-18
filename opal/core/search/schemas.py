from opal.core.search.search_rule import SearchRule
from opal.core.schemas import serialize_schema
from opal.core.subrecords import subrecords


def extract_schema():
    custom_rules = [i().to_dict() for i in SearchRule.list()]
    schema = serialize_schema([
        s for s in subrecords() if s._advanced_searchable
    ])
    return sorted(custom_rules + schema, key=lambda x: x["display_name"])
