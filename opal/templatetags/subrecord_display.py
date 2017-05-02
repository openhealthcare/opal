from django import template
from django.template.loader import get_template
register = template.Library()


class SubrecordDisplayNode(template.Node):
    def __init__(self, subrecord, prefixes=None):
        self.subrecord = subrecord
        self.prefixes = prefixes

    def render(self, context):
        subrecord = self.subrecord.resolve(context)
        if self.prefixes:
            prefixes = self.prefixes.resolve(context)
            template_name = subrecord.get_display_template(
                list_prefixes=prefixes
            )
        else:
            template_name = subrecord.get_display_template()

        t = get_template(template_name)
        return t.render(context)


def subrecord_display(parser, token):
    """
        a template tag that takes in a bunch of path prefixes
        and looks for a subrecord display template with those
        prefixes or its own.

        e.g.
        {% subrecord_display models.Demographics '["someTag"]' %}
    """

    tokens = token.split_contents()
    prefixes = tokens[2]

    if prefixes:
        prefixes = parser.compile_filter(prefixes)

    return SubrecordDisplayNode(
        parser.compile_filter(tokens[1]),
        prefixes
    )

register.tag('subrecord_display', subrecord_display)
