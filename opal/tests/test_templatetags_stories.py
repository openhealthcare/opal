"""
Unittests for opal.templatetags.stories
"""
from opal.core.test import OpalTestCase

from opal.templatetags import stories

class StoryTestCase(OpalTestCase):
    def test_story(self):
        expected = dict(label='test', stories=[])
        self.assertEqual(expected, stories.story('test', 'foo'))
