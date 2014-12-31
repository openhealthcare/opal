"""
Templatetags for form/modal helpers
"""
from django import template

register = template.Library()

def _visibility_clauses(show, hide):
    """
    Given the show/hide clauses of an element's **kwargs,
    construct the angular directives to insert into the template.
    """
    visibility = None
    if hide: 
        visibility = 'ng-hide="{0}"'.format(hide)
    if show: 
        show = ' ng-show="{0}"'.format(show)
        if visibility:
            visibility += show
        else:
            visibility = show
    return visibility

def _icon_classes(name):
    """
    Given the name of an icon, return the classes that will render it
    """
    if name.startswith('fa-'):
        return 'fa ' + name
    if name.startswith('glyphicon'):
        return 'glyphicon ' + name
    return name

def _input(*args, **kwargs):
    model = kwargs.pop('model')
    label = kwargs.pop('label')
    lookuplist = kwargs.pop('lookuplist', None)
    icon = kwargs.pop('icon', None)
    if icon:
        icon = _icon_classes(icon)
        
    visibility = _visibility_clauses(kwargs.pop('show', None),
                                     kwargs.pop('hide', None))
    
    return {
        'label'     : label,
        'model'     : model,
        'directives': args,
        'lookuplist': lookuplist,
        'visibility': visibility,
        'icon'      : icon
    }

@register.inclusion_tag('_helpers/input.html')
def input(*args, **kwargs):
    """
    Render a text input

    Kwargs: 
    - hide : Condition to hide
    - show : Condition to show
    - model: Angular model
    - label: User visible label
    - lookuplist: Name of the lookuplist
    """
    return _input(*args, **kwargs)

@register.inclusion_tag('_helpers/input.html')
def datepicker(*args, **kwargs):
    return _input(*[a for a in args] + ["bs-datepicker"], **kwargs)

@register.inclusion_tag('_helpers/select.html')
def select(*args, **kwargs):
    """
    Render a dropdown element

    Kwargs: 
    - hide : Condition to hide
    - show : Condition to show
    - model: Angular model
    - label: User visible label
    - lookuplist: Name of the lookuplist
    """
    model = kwargs.pop('model')
    label = kwargs.pop('label')
    lookuplist = kwargs.pop('lookuplist', None)
    visibility = _visibility_clauses(kwargs.pop('show', None),
                                     kwargs.pop('hide', None))
    return {
        'label'     : label,
        'model'     : model,
        'directives': args,
        'lookuplist': lookuplist,
        'visibility': visibility
    }

@register.inclusion_tag('_helpers/textarea.html')
def textarea(*args, **kwargs):
    return {
        'label': kwargs.pop('label', None),
        'model': kwargs.pop('model', None),    
    }

@register.inclusion_tag('_helpers/checkbox.html')
def checkbox(*args, **kwargs):
    return {
        'label'     : kwargs.pop('label', None),
        'model'     : kwargs.pop('model', None),
        'width'     : kwargs.pop('width', 8),
        'labelwidth': kwargs.pop('labelwidth', 3)
    }
