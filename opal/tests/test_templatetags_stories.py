"""
Unittests for opal.templatetags.stories
"""
from mock import patch
from opal.core.test import OpalTestCase

from opal.templatetags import stories

class StoryTestCase(OpalTestCase):

    def test_story(self):
        with patch('os.walk') as mockwalk:
            mockwalk.return_value = [
                ('/foo', ('bar',), ('baz~',)),
            ]

            expected = dict(label='test', stories=[])
            self.assertEqual(expected, stories.story('test', 'foo'))
