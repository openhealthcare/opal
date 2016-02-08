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


def extract_common_args(kwargs):
    args = {
        "model": kwargs.pop('model', None),
        "label": kwargs.pop('label', None),
        "change": kwargs.pop("change", None),
        "autofocus": kwargs.pop("autofocus", None),
        "help_text": kwargs.pop("help_text", None)
    }

    disabled = kwargs.pop('disabled', None)

    if disabled:
        args["disabled"] = disabled

    return args


def _input(*args, **kwargs):
    ctx = extract_common_args(kwargs)
    lookuplist = kwargs.pop('lookuplist', None)
    icon = kwargs.pop('icon', None)
    required = kwargs.pop('required', False)
    formname = kwargs.pop('formname', None)
    unit = kwargs.pop('unit', None)
    data = kwargs.pop('data', [])
    enter = kwargs.pop('enter', None)
    maxlength = kwargs.pop('maxlength', None)

    if required:
        if not formname:
            raise ValueError('You must pass formname if you pass required')

    if icon:
        icon = _icon_classes(icon)

    visibility = _visibility_clauses(kwargs.pop('show', None),
                                     kwargs.pop('hide', None))

    ctx.update({
        'modelname' : ctx["model"].replace('.', '_'),
        'directives': args,
        'lookuplist': lookuplist,
        'visibility': visibility,
        'icon'      : icon,
        'required'  : required,
        'formname'  : formname,
        'unit'      : unit,
        'data'      : data,
        'enter'     : enter,
        'maxlength' : maxlength
    })

    return ctx


@register.inclusion_tag('_helpers/checkbox.html')
def checkbox(*args, **kwargs):
    ctx = extract_common_args(kwargs)
    return ctx


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
    - required: label to show when we're required!
    """
    return _input(*args, **kwargs)

@register.inclusion_tag('_helpers/input.html')
def datepicker(*args, **kwargs):
    if 'mindate' in kwargs:
        kwargs['data'] = [
            ('min-date', kwargs['mindate'])
        ]
    return _input(*[a for a in args] + ["bs-datepicker"], **kwargs)

@register.inclusion_tag('_helpers/radio.html')
def radio(*args, **kwargs):
    visibility = _visibility_clauses(kwargs.pop('show', None),
                                     kwargs.pop('hide', None))
    ctx = extract_common_args(kwargs)

    ctx.update({
        'lookuplist': kwargs.pop('lookuplist', None),
        'visibility': visibility
    })

    return ctx


@register.inclusion_tag('_helpers/select.html')
def select(*args, **kwargs):
    """
    Render a dropdown element

    Kwargs:
    - hide : Condition to hide
    - show : Condition to show
    - model: Angular model
    - label: User visible label
    - lookuplist: Name or value of the lookuplist
    - other: (False) Boolean to indicate that we should allow free text if the item is not in the list
    """
    ctx = extract_common_args(kwargs)
    lookuplist = kwargs.pop('lookuplist', None)
    form_name = kwargs.pop('formname', "form")
    other = kwargs.pop('other', False)
    help_template = kwargs.pop('help', None)
    help_text = kwargs.pop('help_text', None)
    placeholder = kwargs.pop("placeholder", None)
    required = kwargs.pop('required', False)
    visibility = _visibility_clauses(kwargs.pop('show', None),
                                     kwargs.pop('hide', None))
    default_null = kwargs.pop('default_null', True)
    tagging = kwargs.pop('tagging', True)
    multiple = kwargs.pop('multiple', False)

    if required:
        if not form_name:
            raise ValueError('You must pass formname if you pass required')

    if lookuplist is None:
        other_show = None
    else:
        other_show = "{1} != null && {0}.indexOf({1}) == -1".format(lookuplist, ctx["model"])
    other_label = '{0} Other'.format(ctx["label"])

    ctx.update({
        'placeholder': placeholder,
        'default_null': default_null,
        'form_name': form_name,
        'directives': args,
        'lookuplist': lookuplist,
        'visibility': visibility,
        'help_template': help_template,
        'help_text': help_text,
        'other': other,
        'model_name': ctx["model"].replace('.', '_').replace('[','').replace(']', ''),
        'required': required,
        'other_show': other_show,
        'other_label': other_label,
        'tagging': tagging,
        'multiple': multiple,
    })

    return ctx

@register.inclusion_tag('_helpers/textarea.html')
def textarea(*args, **kwargs):
    visibility = _visibility_clauses(kwargs.pop('show', None),
                                     kwargs.pop('hide', None))

    ctx = extract_common_args(kwargs)
    ctx.update({
        'macros'    : kwargs.pop('macros', False),
        'visibility': visibility

    })

    return ctx

@register.inclusion_tag('_helpers/icon.html')
def icon(name):
    if name.startswith('glyphicon'):
        icon = 'glyphicon ' + name
    if name.startswith('fa'):
        icon = 'fa ' + name
    return dict(icon=icon)


@register.inclusion_tag('_helpers/process_steps.html')
def process_steps(*args, **kwargs):
    """
    renders a set of steps for a multi stage form

    kwargs
    "show_index" do we show the index number of the step we're on
    "process_steps" an angular scoped array name with the fields "icon" and
    "title" (title is optional)
    "complete" an angular expression to tell us if the process step is complete
    "disabled" an angular expression to tell us if the process step is disabled
    "active" an angular expression to tell us if the process step is active
    """
    required_kwargs = ["process_steps", "complete", "disabled", "active"]
    template_args = {}
    for required_kwarg in required_kwargs:
        template_args[required_kwarg] = kwargs.pop(required_kwarg)

    template_args["show_index"] = kwargs.pop("show_index", False)
    template_args["show_titles"] = kwargs.pop("show_index", False)
    return template_args
