"""
Templatetags for panels
"""
import copy

from django import template

from opal.models import PatientSubrecord
from opal.utils import camelcase_to_underscore

register = template.Library()


@register.inclusion_tag('templatetags/panels/record_panel.html', takes_context=True)
def record_panel(context, model, only_display_if_exists=False):
    """
    Register a panel for our record.
    Editable is an angular expression
    to be evaluated
    """
    context = copy.copy(context)
    patient = context['patient']
    episode = None
    Model = model.__class__

    if issubclass(Model, PatientSubrecord):
        records = Model.objects.filter(patient=patient)
    else:
        episode = context['episode']
        records = Model.objects.filter(episode=episode)

    ctx = {
        'model'                 : model,
        'episode'               : episode,
        'patient'               : patient,
        'records'               : records,
        'singleton'             : getattr(model, '_is_singleton', False),
        'only_display_if_exists': only_display_if_exists,
    }

    context.dicts.append(ctx)
    return context
