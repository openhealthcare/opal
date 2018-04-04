"""
Unittests for opal.templatetags.stories
"""
import os

from django.test import override_settings
from mock import patch
from opal.core.test import OpalTestCase

from opal.templatetags import stories

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['/tmp'],
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'opal.context_processors.settings',
                'opal.context_processors.models'
            ],
            # ... some options here ...
        },
    },
]

class StoryTestCase(OpalTestCase):

    @override_settings(TEMPLATES = TEMPLATES)
    def test_story_with_dirs(self):
        with patch.object(stories, 'get_app_template_dirs') as mock_dirs:
            mock_dirs.return_value = []
            with patch('os.walk') as mockwalk:
                mockwalk.return_value = [
                    ('/foo', ('bar',), ('baz~','baz')),
                ]
                expected = dict(label='test', stories=[os.path.join('foo', 'baz')])
                self.assertEqual(expected, stories.story('test', 'foo'))


    def test_story_with_app_dirs(self):
        expected = dict(label='test', stories=[])
        self.assertEqual(expected, stories.story('test', 'foo'))
