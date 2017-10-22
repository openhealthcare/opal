from __future__ import unicode_literals

import copy

from django import template
register = template.Library()


def add_common_context(context, subrecord):
    context = copy.copy(context)
    ctx = {}
    ctx["subrecord"] = subrecord
    ctx["model"] = "editing.{}".format(subrecord.get_api_name())
    context.update(ctx)
    return context


@register.inclusion_tag('_helpers/multisave.html', takes_context=True)
def multisave(context, subrecord):
    return add_common_context(context, subrecord)


@register.inclusion_tag(
    '_helpers/collapsed_multisave.html', takes_context=True
)
def collapsed_multisave(context, subrecord):
    return add_common_context(context, subrecord)
