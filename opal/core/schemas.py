"""
Utilities for dealing with OPAL Schemas
"""
from opal.utils import stringport
from opal.core.subrecords import subrecords
from opal.core import application, plugins
from opal import models

app = application.get_app()

schema = stringport(app.schema_module)

def serialize_model(model):
    col = {
        'name'        : model.get_api_name(),
        'display_name': model.get_display_name(),
        'single'      : model._is_singleton,
        'advanced_searchable': model._advanced_searchable,
        'fields'      : model.build_field_schema()
        }
    if hasattr(model, '_sort'):
        col['sort'] = model._sort
    if hasattr(model, '_modal'):
        col['modal_size'] = model._modal
    if hasattr(model, '_read_only'):
        col['readOnly'] = model._read_only
    return col

def serialize_schema(schema):
    return [serialize_model(column) for column in schema]

def _get_plugin_schemas():
    scheme = {}
    for plugin in plugins.plugins():
        scheme.update(plugin().list_schemas())
    return scheme

def _get_list_schema():
    schemas = _get_field_names(schema.list_schemas)

    plugin_schemas = _get_plugin_schemas()
    schemas.update(_get_field_names(plugin_schemas))
    return schemas

def _get_field_names(schemas):
    scheme = {}
    for name, s in schemas.items():
        if isinstance(s, list):
            try:
                scheme[name] = [f.get_api_name() for f in s]
            except:
                raise
        else:
            scheme[name] = _get_field_names(s)
    return scheme

def _get_all_fields():
    response = {
        subclass.get_api_name(): serialize_model(subclass)
        for subclass in subrecords()
    }
    response['tagging'] = serialize_model(models.Tagging)
    return response

def list_records():
    return _get_all_fields()

def list_schemas():
    """
    Return a JSON representation of our list schemas and all fields
    """
    return _get_list_schema()

def extract_schema():
    return serialize_schema([models.Tagging] + [c for c in subrecords()])

def get_all_list_schema_classes():
    schemas = schema.list_schemas.copy()
    schemas.update(_get_plugin_schemas())
    return schemas
