"""
Templatetags for Patient Lists
"""
from __future__ import unicode_literals

from django import template

register = template.Library()


@register.inclusion_tag('patient_lists/tabbed_list_group.html',
                        takes_context=True)
def tabbed_list_group(context):
    group = context['list_group']
    user = context['request'].user
    members = group.get_member_lists_for_user(user)
    active_list = context['patient_list']
    return dict(
        active_list=active_list,
        members=members,
    )
