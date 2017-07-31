"""
Templatetags for panels
"""
import copy

from django import template
from opal.core.subrecords import patient_subrecords

from opal.utils import camelcase_to_underscore

register = template.Library()


@register.inclusion_tag('_helpers/record_panel.html', takes_context=True)
def record_panel(
    context,
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
    context = copy.copy(context)

    if name is None:
        if isinstance(model, str):
            raise ValueError("Unable to find a subrecord")
        name = model.get_api_name()

    if detail_template is None:
        detail_template = model.get_detail_template()

    if title is None:
        title = model.get_display_name()

    ctx = {
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

    context.dicts.append(ctx)
    return context


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


@register.inclusion_tag('_helpers/aligned_pair.html')
def aligned_pair(model, label=None):
    return {
        'model': model,
        'label': label
    }


@register.inclusion_tag(
    '_helpers/cached_subrecord_modal.html', takes_context=True
)
def cached_subrecord_modal(context, subrecord, prefix=None):
    """
        renders a text in the angular template format
        ie
        <script type="text/ng-template" id="/tpl.html">
            Content of the template.
        </script>

        if you put in a model and a patient list
        it will do the reverse logic for you
    """
    child_context = copy.copy(context)
    child_context.update(dict(
        url=subrecord.get_modal_url(prefix),
        template=subrecord.get_modal_template(prefix),

        # we need to pass in the same context variables as
        # opal.views.ModalTemplateView.get_context_data
        name=subrecord.get_api_name(),
        title=subrecord.get_display_name(),
        icon=subrecord.get_icon(),
        single=subrecord._is_singleton,
        column=subrecord
    ))

    return child_context
