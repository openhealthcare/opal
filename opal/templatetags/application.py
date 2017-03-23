"""
Templatetags for working with Opal applications
"""
import warnings

from django import template

from opal.core import application, plugins

warnings.simplefilter('once', DeprecationWarning)
register = template.Library()


# TODO 0.9.0: Remove this
@register.inclusion_tag('plugins/menuitems.html', takes_context=True)
def application_menuitems(context):
    warnthem = """
opal.templatetags.application.application_menuitems has been replaced
by opal.templatetags.menus and will be removed in Opal 0.9.0

You should replace calls to {% application_menuitems %} with the newer
{% menu %} templatetag.
"""
    warnings.warn(warnthem, DeprecationWarning, stacklevel=2)

    def items():
        app = application.get_app()
        for i in app.get_menu_items(user=context['user']):
            yield i
    return dict(items=items)


@register.inclusion_tag('plugins/javascripts.html')
def core_javascripts(namespace):
    def scripts():
        app = application.get_app()
        for javascript in app.get_core_javascripts(namespace):
            yield javascript
    return dict(javascripts=scripts)


@register.inclusion_tag('plugins/javascripts.html')
def application_javascripts():
    def scripts():
        app = application.get_app()
        for javascript in app.get_javascripts():
            yield javascript
    return dict(javascripts=scripts)


@register.inclusion_tag('plugins/stylesheets.html')
def application_stylesheets():
    def styles():
        app = application.get_app()
        for style in app.get_styles():
            if style.endswith(".scss"):
                mime_type = "text/x-scss"
            else:
                mime_type = "text/css"
            yield style, mime_type
    return dict(styles=styles)


@register.inclusion_tag('plugins/actions.html')
def application_actions():
    def actions():
        app = application.get_app()
        for action in app.actions:
            yield action
        for plugin in plugins.OpalPlugin.list():
            for action in plugin.actions:
                yield action
    return dict(actions=actions)
