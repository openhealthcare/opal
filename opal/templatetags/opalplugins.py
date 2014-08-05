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
            if plugin.javascript_namespace == namespace:
                for javascript in plugin.javascripts:
                    yield javascript
    return dict(javascripts=scripts)
