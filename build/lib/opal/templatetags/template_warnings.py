from django import template
import warnings


register = template.Library()


class WarningNode(template.Node):
    def render(self, context):
        return ''


@register.tag
def warn(parser, token):
    """
    A template tag that lets you insert a warning
    """
    bits = token.split_contents()
    if not len(bits) == 2:
        raise ValueError("Warnings only takes a single string message")
    warnings.warn(bits[1], DeprecationWarning, stacklevel=2)

    return WarningNode()
