"""
Template tag to render a random loading gif
"""
import random

from django import template

register = template.Library()


@register.inclusion_tag('loading_gif.html')
def loading_gif():
    return dict(loading_gif='img/svg-loaders/{0}.svg'.format(
        random.choice([
            'ball-triangle',
            'rings',
            'grid',
            'three-dots',
            'puff',
            'circles'
        ])))
