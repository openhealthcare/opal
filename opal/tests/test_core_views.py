"""
Unittests for opal.core.views
"""

from __future__ import unicode_literals

import six
import datetime
from opal.core import test
from opal.core import views


class SerializerTestCase(test.OpalTestCase):

    def test_serializer_default_will_super(self):
        s = views.OpalSerializer()
        with self.assertRaises(TypeError):
            s.default(None)

    def test_binaries_become_utf_8(self):
        s = views.OpalSerializer()
        binary = 'Hello beautiful world. I am a binary.'.encode()
        serialized = s.default(binary)
        self.assertIsInstance(serialized, six.text_type)

    def test_time_serialisation(self):
        s = views.OpalSerializer()
        serialised = s.default(datetime.time(20))
        self.assertEqual(serialised, "20:00:00")
