"""
Unittests for opal.templatetags.stories
"""
from django.test import override_settings
from mock import patch
from opal.core.test import OpalTestCase

from opal.templatetags import stories

class StoryTestCase(OpalTestCase):

    @override_settings(TEMPLATE_DIRS = ['/tmp'])
    def test_story(self):
        with patch.object(stories, 'get_app_template_dirs') as mock_dirs:
            mock_dirs.return_value = []
            with patch('os.walk') as mockwalk:
                mockwalk.return_value = [
                    ('/foo', ('bar',), ('baz~','baz')),
                ]
                expected = dict(label='test', stories=['foo/baz'])
                self.assertEqual(expected, stories.story('test', 'foo'))
