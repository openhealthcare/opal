"""
Unittests for opal.core.views
"""
import warnings

from opal.core import test

from opal.core import views

class SerializerTestCase(test.OpalTestCase):

    def test_serializer_default_will_super(self):
        s = views.OpalSerializer()
        with self.assertRaises(TypeError):
            s.default(None)


class BuildJSONResponseTestCase(test.OpalTestCase):

    def test_underscore_spelling_warns(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            r = views._build_json_response({})
            self.assertEqual(200, r.status_code)
            assert len(w) == 1
            assert issubclass(w[-1].category, DeprecationWarning)
            assert "will be removed" in str(w[-1].message)
