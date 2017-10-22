from django import template

register = template.Library()


@register.filter
def underscore_to_spaces(value):
    return value.replace("_", " ")
