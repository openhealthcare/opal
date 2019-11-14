"""
Templatetags for form helpers
"""
import json
from django import template
from django.db import models
from opal.core.lookuplists import get_values_from_api_name
from opal.core.subrecords import get_subrecord_from_model_name
from opal.core import fields
from opal.core.serialization import OpalSerializer

register = template.Library()


def _model_and_field_from_path(fieldname):
    model_name, field_name = fieldname.split(".")
    model = get_subrecord_from_model_name(model_name)
    field = None

    if hasattr(model, field_name):
        # this is true for lookuplists
        lookuplist_field = getattr(model, field_name)
        if lookuplist_field.__class__ == fields.ForeignKeyOrFreeText:
            field = lookuplist_field

    if not field:
        field = model._meta.get_field(field_name)
    return model, field


def infer_from_subrecord_field_path(subrecord_field_path):
    _, field_name = subrecord_field_path.split('.')
    model, field = _model_and_field_from_path(subrecord_field_path)

    ctx = {}
    ctx["label"] = model._get_field_title(field_name)
    ctx["model"] = "editing.{0}.{1}".format(
        model.get_api_name(),
        field_name
    )

    if fields.is_numeric(field):
        ctx["element_type"] = "number"

    # for all django fields we'll get an empty list back
    # we default for free text or foreign keys
    enum = model.get_field_enum(field_name)

    if enum:
        ctx["lookuplist"] = enum
    else:
        lookuplist_api_name = model.get_lookup_list_api_name(field_name)
        if lookuplist_api_name:
            ctx["lookuplist"] = get_values_from_api_name(lookuplist_api_name)

    if hasattr(field, "formfield"):
        # TODO remove the blankable condition and make sure
        # all fields are null=False
        blankable = getattr(field, "blank", True)
        ctx["required"] = (not blankable) or field.formfield().required
    else:
        # ForeignKeyOrFreeText are never required at this time
        # so if we can't work out if its required, lets default
        # to false
        ctx["required"] = False

    if hasattr(field, "max_length"):
        ctx["maxlength"] = field.max_length
    return ctx


def _extract_common_args(context, *args, **kwargs):
    if "field" in kwargs:
        args = infer_from_subrecord_field_path(kwargs["field"])
        args['field'] = kwargs['field'].split('.')[1]
    else:
        args = {}

    if "label" in kwargs:
        args["label"] = kwargs["label"]

    args["element_type"] = kwargs.pop(
        'element_type', args.get('element_type', 'text')
    )

    args["required"] = kwargs.pop('required', args.pop("required", False))
    disabled = kwargs.pop('disabled', None)

    if disabled:
        args["disabled"] = disabled


    if context.get('instance', None) is not None:
        args['value'] = getattr(context['instance'], args['field'], None)

    return args


@register.inclusion_tag('templatetags/forms/input.html', takes_context=True)
def input(context, *args, **kwargs):
    """
    Render a text input
    """
    return _extract_common_args(context, *args, **kwargs)


@register.inclusion_tag('templatetags/forms/select.html', takes_context=True)
def select(context, *args, **kwargs):
    """
    Render a dropdown element
    """
    ctx = _extract_common_args(context, *args, **kwargs)
    if kwargs.get('lookuplist'):
        ctx['lookuplist'] = get_values_from_api_name(kwargs['lookuplist'])
    return ctx


@register.inclusion_tag('templatetags/forms/date_of_birth_field.html', takes_context=True)
def date_of_birth_field(context, *args, **kwargs):
    model_name = kwargs.get('model_name', "editing.demographics.date_of_birth")
    return dict(
        model_name=model_name,
    )


@register.inclusion_tag('templatetags/forms/textarea.html', takes_context=True)
def textarea(context, *args, **kwargs):
    ctx = _extract_common_args(context, *args, **kwargs)
    ctx["rows"] = kwargs.pop("rows", 5)
    return ctx


@register.inclusion_tag('templatetags/forms/checkbox.html', takes_context=True)
def checkbox(context, *args, **kwargs):
    ctx = _extract_common_args(context, *args, **kwargs)
    return ctx


@register.inclusion_tag('templatetags/forms/datepicker.html', takes_context=True)
def datepicker(context, *args, **kwargs):
    context = _extract_common_args(context, *args, **kwargs)
    return context
