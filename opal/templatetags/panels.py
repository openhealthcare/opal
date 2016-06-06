"""
Templatetags for panels
"""
from django import template
from opal.core.subrecords import patient_subrecords

from opal.utils import camelcase_to_underscore

register = template.Library()


@register.inclusion_tag('_helpers/record_panel.html')
def record_panel(
    model,
    editable=1,
    title=None,
    name=None,
    detail_template=None,
    angular_filter=None,
    noentries=None,
    only_display_if_exists=False,
    full_width=False,
):
    """
    Register a panel for our record.
    Editable is an angular expression
    to be evaluated
    """

    if name is None:
        if isinstance(model, str):
            raise ValueError("Unable to find a subrecord")
        name = model.get_api_name()

    if detail_template is None:
        detail_template = model.get_detail_template()

    if title is None:
        title = model.get_display_name()

    return {
        'name': name,
        'singleton': getattr(model, '_is_singleton', False),
        'title': title,
        'detail_template': detail_template,
        'icon': model.get_icon(),
        'editable': editable,
        'angular_filter': angular_filter,
        'noentries': noentries,
        'only_display_if_exists': only_display_if_exists,
        'full_width': full_width,
        'is_patient_subrecord': model.__class__ in patient_subrecords()
    }


@register.inclusion_tag('_helpers/record_timeline.html')
def record_timeline(model, whenfield):
    name = camelcase_to_underscore(model.__class__.__name__)

    return {
        'name': name,
        'editable': True,
        'title': getattr(model, '_title', name.replace('_', ' ').title()),
        'detail_template': model.__class__.get_detail_template(),
        'icon': getattr(model, '_icon', None),
        'whenfield': whenfield,
    }

@register.inclusion_tag('_helpers/teams_panel.html')
def teams_panel():
    return {}
