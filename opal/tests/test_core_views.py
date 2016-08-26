"""
Unittests for opal.core.views
"""
from opal.core import test

from opal.core import views

class SerializerTestCase(test.OpalTestCase):

    def test_serializer_default_will_super(self):
        s = views.OpalSerializer()
        with self.assertRaises(TypeError):
            s.default(None)
