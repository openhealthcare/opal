"""
Templatetags for form/modal helpers
"""
from django import template

register = template.Library()

@register.inclusion_tag('_helpers/input.html')
def input(*args, **kwargs):
    """
    Render a text input
    """
    model = kwargs.pop('model')
    label = kwargs.pop('label')
    lookuplist = kwargs.pop('lookuplist', None)
    return {
        'label'     : label,
        'model'     : model,
        'directives': args,
        'lookuplist': lookuplist
    }

@register.inclusion_tag('_helpers/select.html')
def select(*args, **kwargs):
    """
    Render a dropdown element
    """
    model = kwargs.pop('model')
    label = kwargs.pop('label')
    lookuplist = kwargs.pop('lookuplist', None)
    return {
        'label'     : label,
        'model'     : model,
        'directives': args,
        'lookuplist': lookuplist
    }

@register.inclusion_tag('_helpers/textarea.html')
def textarea(*args, **kwargs):
    return {
        'label': kwargs.pop('label', None),
        'model': kwargs.pop('model', None),
        
    }
