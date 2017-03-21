"""
Templatetags for rendering menus in Opal applications
"""
import copy

from django import template

from opal.core import application

register = template.Library()


@register.inclusion_tag('templatetags/menus/menu.html', takes_context=True)
def menu(context, classes):
    """
    Render the menu for this application.
    """
    context = copy.copy(context)
    app = application.get_app()
    menu = app.get_menu(user=context['user'])

    context.dicts.append({
        'classes': classes,
        'menu'   : menu,
    })
    return context
