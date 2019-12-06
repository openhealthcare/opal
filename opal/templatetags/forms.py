"""
Templatetags for form/modal helpers
"""
import json
from django import template
from django.db import models
from opal.core.subrecords import get_subrecord_from_model_name
from opal.core import fields
from opal.core.serialization import OpalSerializer

register = template.Library()


def get_style(kwargs):
    """
    Return the style of this widget.
    """
    style = kwargs.get('style', 'horizontal')
    valid_styles = ['horizontal', 'vertical']
    if style not in valid_styles:
        raise ValueError('{0} is not a valid form style!'.format(style))
    return style


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


def infer_from_subrecord_field_path(subRecordFieldPath):
    _, field_name = subRecordFieldPath.split('.')
    model, field = _model_and_field_from_path(subRecordFieldPath)

    ctx = {}
    ctx["label"] = model._get_field_title(field_name)
    ctx["model"] = "editing.{0}.{1}".format(
        model.get_api_name(),
        field_name
    )
    ctx['element_name'] = "editing.{0}._client.id + '_{1}'".format(
        model.get_api_name(),
        field_name
    )

    if fields.is_numeric(field):
        ctx["element_type"] = "number"

    # for all django fields we'll get an empty list back
    # we default for free text or foreign keys
    enum = model.get_field_enum(field_name)

    if enum:
        ctx["lookuplist"] = json.dumps(enum, cls=OpalSerializer)
    else:
        lookuplist_api_name = model.get_lookup_list_api_name(field_name)
        if lookuplist_api_name:
            ctx["lookuplist"] = "{}_list".format(lookuplist_api_name)

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


def extract_common_args(kwargs):
    if "field" in kwargs:
        args = infer_from_subrecord_field_path(kwargs["field"])
    else:
        args = {}

    for field in ["model", "label", "change"]:
        if field in kwargs:
            args[field] = kwargs[field]

    element_name = kwargs.pop('element_name', args.get('element_name'))
    args["element_type"] = kwargs.pop(
        'element_type', args.get('element_type', 'text')
    )

    if element_name:
        args["element_name"] = element_name
    else:
        model_name = args["model"].replace('.', '_').replace("editing_", "")
        model_name = model_name.replace("[", "").replace("]", "")
        args["element_name"] = "'{}'".format(model_name)

    args["autofocus"] = kwargs.pop("autofocus", None)
    args["help_text"] = kwargs.pop("help_text", None)
    args["formname"] = kwargs.pop('formname', 'form')
    args["visibility"] = _visibility_clauses(
        kwargs.pop('show', None), kwargs.pop('hide', None)
    )
    args["style"] = get_style(kwargs)
    # required could have been set via the model
    args["required"] = kwargs.pop('required', args.pop("required", False))
    disabled = kwargs.pop('disabled', None)

    if disabled:
        args["disabled"] = disabled

    return args


@register.inclusion_tag('_helpers/datetime_picker.html')
def datetimepicker(*args, **kwargs):
    ctx = extract_common_args(kwargs)
    ctx["date_picker_args"] = [('date-type', 'date',), ('autoclose', 1,), ]
    ctx["date_label"] = kwargs.pop("date_label", "Date")
    ctx["time_label"] = kwargs.pop("time_label", "Time")
    return ctx


def _input(*args, **kwargs):
    ctx = extract_common_args(kwargs)

    if "lookuplist" in kwargs:
        ctx["lookuplist"] = kwargs.pop("lookuplist")

    icon = kwargs.pop('icon', None)
    unit = kwargs.pop('unit', None)
    data = kwargs.pop('data', [])
    enter = kwargs.pop('enter', None)
    maxlength = kwargs.pop('maxlength', None) or ctx.get("maxlength")
    datepicker = kwargs.pop("datepicker", False)

    if icon:
        icon = _icon_classes(icon)

    ctx.update({
        'directives': args,
        'icon'      : icon,
        'unit'      : unit,
        'data'      : data,
        'enter'     : enter,
        'maxlength' : maxlength,
        'datepicker': datepicker,
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


@register.inclusion_tag('_helpers/datepicker.html')
def datepicker(*args, **kwargs):
    kwargs["datepicker"] = True
    context = _input(*args, **kwargs)
    if 'mindate' in kwargs:
        context['mindate'] = kwargs['mindate']
    context["user_options"] = kwargs.pop("user_options", False)
    return context


@register.inclusion_tag('_helpers/timepicker.html')
def timepicker(*args, **kwargs):
    return extract_common_args(kwargs)


def _radio(*args, **kwargs):
    ctx = extract_common_args(kwargs)
    ctx["lookuplist"] = kwargs.pop("lookuplist", ctx.get("lookuplist", None))
    return ctx


@register.inclusion_tag('_helpers/radio.html')
def radio(*args, **kwargs):
    return _radio(*args, **kwargs)


@register.inclusion_tag('_helpers/radio_vertical.html')
def radio_vertical(*args, **kwargs):
    return _radio(*args, **kwargs)


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
    - other: (False) Boolean to indicate that we should allow free text if the
             item is not in the list
    """
    ctx = extract_common_args(kwargs)
    lookuplist = kwargs.pop("lookuplist", ctx.get("lookuplist", None))

    other = kwargs.pop('other', False)
    help_template = kwargs.pop('help', None)
    placeholder = kwargs.pop("placeholder", None)
    default_null = kwargs.pop('default_null', True)
    tagging = kwargs.pop('tagging', True)
    multiple = kwargs.pop('multiple', False)

    if lookuplist is None:
        other_show = None
    else:
        other_show = "{1} != null && {0}.indexOf({1}) == -1".format(
            lookuplist, ctx["model"])
    other_label = '{0} Other'.format(ctx["label"])

    ctx.update({
        'lookuplist': lookuplist,
        'placeholder': placeholder,
        'default_null': default_null,
        'directives': args,
        'help_template': help_template,
        'other': other,
        'other_show': other_show,
        'other_label': other_label,
        'tagging': tagging,
        'multiple': multiple,
    })

    return ctx


@register.inclusion_tag('_helpers/textarea.html')
def textarea(*args, **kwargs):
    ctx = extract_common_args(kwargs)
    ctx["rows"] = kwargs.pop("rows", 5)
    return ctx


@register.inclusion_tag('_helpers/static.html')
def static(fieldname):
    _, field_name = fieldname.split('.')
    model, field = _model_and_field_from_path(fieldname)
    return dict(
        model="editing.{0}.{1}".format(model.get_api_name(),
                                       field_name),
        label=model._get_field_title(field_name),
        datep=isinstance(field, models.DateField)
    )


@register.inclusion_tag('_helpers/icon.html')
def icon(name):
    icon = name
    if name.startswith('glyphicon'):
        icon = 'glyphicon ' + name
    if name.startswith('fa'):
        icon = 'fa ' + name
    return dict(icon=icon)


@register.inclusion_tag('_helpers/date_of_birth_field.html')
def date_of_birth_field(**kwargs):
    model_name = kwargs.get('model_name', "editing.demographics.date_of_birth")
    return dict(
        model_name=model_name,
        style=get_style(kwargs)
    )


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
    template_args["show_titles"] = kwargs.pop("show_titles", False)
    return template_args
