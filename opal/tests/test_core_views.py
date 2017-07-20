"""
Unittests for opal.core.views
"""
import warnings

import six

from opal.core import test

from opal.core import views

class SerializerTestCase(test.OpalTestCase):

    def test_serializer_default_will_super(self):
        s = views.OpalSerializer()
        with self.assertRaises(TypeError):
            s.default(None)

    def test_binaries_become_utf_8(self):
        s = views.OpalSerializer()
        binary = six.b('Hello beautiful world. I am a binary.')
        serialized = s.default(binary)
        self.assertIsInstance(serialized, six.text_type)
