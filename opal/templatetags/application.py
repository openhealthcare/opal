"""
Templatetags for working with Opal applications
"""
from django import template

from opal.core import application, plugins

register = template.Library()


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


@register.inclusion_tag('plugins/angular_module_deps.html')
def opal_angular_deps():
    app = application.get_app()
    return dict(deps=app.get_all_angular_module_deps())
