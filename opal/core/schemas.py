"""
Utilities for dealing with OPAL Schemas
"""
import itertools
from opal.core.subrecords import subrecords
from opal import models


def serialize_model(model):
    col = {
        'name'        : model.get_api_name(),
        'display_name': model.get_display_name(),
        'single'      : model._is_singleton,
        'advanced_searchable': model._advanced_searchable,
        'fields'      : model.build_field_schema(),
        }
    if hasattr(model, '_sort'):
        col['sort'] = model._sort
    if hasattr(model, '_read_only'):
        col['readOnly'] = model._read_only
    if hasattr(model, '_angular_service'):
        col['angular_service'] = model._angular_service
    if hasattr(model, 'get_form_url'):
        col["form_url"] = model.get_form_url()
    if hasattr(model, 'get_icon'):
        col["icon"] = model.get_icon()

    return col


def serialize_schema(schema):
    return [serialize_model(column) for column in schema]


def get_serialised_subrecords():
    extract_subrecords = (
        i for i in subrecords() if i._serialisable
    )
    return serialize_schema(
        itertools.chain([models.Tagging], extract_subrecords)
    )


def list_records():
    """
    This populates the schema api providing the meta field
    information for every subrecord
    """
    serialised_subrecords = get_serialised_subrecords()
    return {
        subrecord["name"]: subrecord for subrecord in serialised_subrecords
    }


def extract_schema():
    """
    This populates the data used by the extract fields api
    """
    return get_serialised_subrecords()
