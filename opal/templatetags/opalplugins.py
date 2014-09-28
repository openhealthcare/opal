"""
Templatetags for including OPAL plugins
"""
from django import template

from opal.utils import OpalPlugin

register = template.Library()

@register.inclusion_tag('plugins/javascripts.html')
def plugin_javascripts(namespace):
    def scripts():
        for plugin in OpalPlugin.__subclasses__():
            if namespace in plugin.javascripts:
                for javascript in plugin.javascripts[namespace]:
                    yield javascript
    return dict(javascripts=scripts)

@register.inclusion_tag('plugins/menuitems.html')
def plugin_menuitems():
    def items():
        for plugin in OpalPlugin.__subclasses__():
            for i in plugin.menuitems:
                yield i
    return dict(items=items)
