"""
Templatetags for working with Opal plugins
"""
import itertools
import warnings

from django import template

from opal.core import plugins, application

warnings.simplefilter('once', DeprecationWarning)
register = template.Library()


@register.inclusion_tag('plugins/javascripts.html')
def plugin_javascripts(namespace):
    def scripts():
        for plugin in plugins.OpalPlugin.list():
            if namespace in plugin.get_javascripts():
                for javascript in plugin.javascripts[namespace]:
                    yield javascript
    return dict(javascripts=scripts)


@register.inclusion_tag('plugins/stylesheets.html')
def plugin_stylesheets():
    def styles():
        for plugin in plugins.OpalPlugin.list():
            for style in plugin.get_styles():
                if style.endswith(".scss"):
                    mime_type = "text/x-scss"
                else:
                    mime_type = "text/css"
                yield style, mime_type
    return dict(styles=styles)


@register.inclusion_tag('plugins/head_extra.html', takes_context=True)
def plugin_head_extra(context):
    def templates():
        for plugin in plugins.OpalPlugin.list():
            for tpl in plugin.head_extra:
                    yield tpl
    ctx = context
    ctx['head_extra'] = templates
    return ctx


# TODO 0.9.0: Remove this
def sort_menu_items(items):
    # sorting of menu item is done withan index
    # property (lower = first), if they don't
    # have an index or if there are multiple with the
    # same index then its done alphabetically

    def alphabetic(x):
        return x["display"]

    def index_sorting(x):
        return x.get("index", 100)

    return sorted(sorted(items, key=alphabetic), key=index_sorting)


# TODO 0.9.0: Remove this
@register.inclusion_tag('plugins/menuitems.html')
def plugin_menuitems():
    warnthem = """
opal.templatetags.plugins.plugin_menuitems has been replaced
by opal.templatetags.menus and will be removed in Opal 0.9.0

You should replace calls to {% plugin_menuitems %} with the newer
{% menu %} templatetag.
"""
    warnings.warn(warnthem, DeprecationWarning, stacklevel=2)

    def items():
        for plugin in plugins.OpalPlugin.list():
            for i in plugin.menuitems:
                yield i

    return dict(items=sort_menu_items(items()))


@register.inclusion_tag('plugins/angular_module_deps.html')
def plugin_opal_angular_deps():
    def deps():
        for plugin in plugins.OpalPlugin.list():
            for i in plugin.angular_module_deps:
                yield i
    return dict(deps=deps)


@register.inclusion_tag('plugins/angular_exclude_tracking.html')
def plugin_opal_angular_tracking_exclude():
    def yield_property(property_name):
        app = application.get_app()
        app_and_plugins = itertools.chain(plugins.OpalPlugin.list(), [app])

        for plugin in app_and_plugins:
            excluded_tracking_prefixes = getattr(plugin, property_name, [])
            for i in excluded_tracking_prefixes:
                yield i

    return dict(
        excluded_tracking_prefix=yield_property(
            "opal_angular_exclude_tracking_prefix"),
        excluded_tracking_qs=yield_property(
            "opal_angular_exclude_tracking_qs")
    )
