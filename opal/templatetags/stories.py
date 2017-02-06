"""
Templatetags for user story / acceptance
"""
import os

from django import template
from django.conf import settings
from django.template.loaders.app_directories import get_app_template_dirs

register = template.Library()


@register.inclusion_tag('_helpers/story.html')
def story(label, story_dir):
    ctx = {
        'label': label
    }

    template_files = []
    for template_dir in (settings.TEMPLATE_DIRS + get_app_template_dirs('')):
        story_path = os.path.join(template_dir, story_dir)
        for dir, dirnames, filenames in os.walk(story_path):
            for filename in filenames:
                if filename.endswith('~'):
                    continue
                template_files.append(os.path.join(story_dir, filename))

    ctx['stories'] = template_files
    return ctx
