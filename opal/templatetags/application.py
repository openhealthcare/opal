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


def get_mime_type(stylesheet):
    """
    Return the appropriate mime type for the stylesheet
    """
    if stylesheet.endswith(".scss"):
        return "text/x-scss"
    else:
        return "text/css"


@register.inclusion_tag('plugins/stylesheets.html')
def core_stylesheets(namespace):
    app = application.get_app()

    def styles():
        for style, media in app.get_core_styles(namespace):
            yield style, get_mime_type(style), media

    return dict(styles=styles)


@register.inclusion_tag('plugins/stylesheets.html')
def application_stylesheets():
    def styles():
        app = application.get_app()
        for style in app.get_styles():
            yield style, get_mime_type(style), "screen"
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
