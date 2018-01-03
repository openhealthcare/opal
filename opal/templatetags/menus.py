"""
Templatetags for rendering menus in Opal applications
"""
from django import template

from opal.core import application

register = template.Library()


@register.inclusion_tag('templatetags/menus/menu.html', takes_context=True)
def menu(context):
    """
    Render the menu for this application.
    """
    app = application.get_app()
    menu = app.get_menu(user=context.get('user', None))
    context['menu'] = menu
    return context
