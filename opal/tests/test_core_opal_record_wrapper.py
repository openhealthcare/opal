import mock
from opal.core.test import OpalTestCase
from opal.core.opal_record_wapper import OpalRecordWrapper
from opal.tests import models as test_models
from opal import models as opal_models


class OpalRecordWrapperTestCase(OpalTestCase):

    def get_with_class_attrs(self, **kwargs):
        class B(OpalRecordWrapper):
            pass

        for i, v in kwargs.items():
            setattr(B, i, v)

        return B

    def test_init_nothing_pass_in(self):
        opal_wrapper = OpalRecordWrapper()
        self.assertIsNone(opal_wrapper.model)
        self.assertIsNone(opal_wrapper.api_name)
        self.assertIsNone(opal_wrapper.display_name)
        self.assertIsNone(opal_wrapper.icon)
        self.assertIsNone(opal_wrapper.template)

    def test_init_class_attributes_overriden_by_passed_in_attrs(self):
        opal_wrapper_cls = self.get_with_class_attrs(
            model=test_models.Birthday,
            api_name="class_api_name",
            display_name="class Api Name",
            icon="class icon",
            template="class template"
        )
        opal_wrapper = opal_wrapper_cls(
            model=test_models.HatWearer,
            api_name="overridden_api_name",
            display_name="overridden Api Name",
            icon="overridden icon",
            template="overridden template"
        )
        self.assertEqual(
            opal_wrapper.model, test_models.HatWearer
        )

        self.assertEqual(
            opal_wrapper.api_name, "overridden_api_name",
        )

        self.assertEqual(
            opal_wrapper.display_name, "overridden Api Name",
        )

        self.assertEqual(
            opal_wrapper.icon, "overridden icon",
        )

        self.assertEqual(
            opal_wrapper.template, "overridden template",
        )

    def test_passed_in_model_is_used_over_class_model(self):
        opal_wrapper_cls = self.get_with_class_attrs(
            model=test_models.Birthday
        )
        opal_wrapper = opal_wrapper_cls(model=test_models.Colour)
        self.assertEqual(
            opal_wrapper.model, test_models.Colour
        )

    def get_tests(
        self, method, attribute, model_method
    ):
        """
        tests all the combinations for the get_ methods
        """
        # test with none
        self.assertIsNone(
            getattr(OpalRecordWrapper(), method)()
        )

        # test populated
        opal_wrapper = OpalRecordWrapper(**{attribute: "something"})
        self.assertEqual(
            getattr(opal_wrapper, method)(),
            "something"
        )

        # test with model
        with mock.patch.object(test_models.HatWearer, model_method) as o:
            o.return_value = "model result"
            opal_wrapper = OpalRecordWrapper(model=test_models.HatWearer)
            self.assertEqual(
                getattr(opal_wrapper, method)(),
                "model result"
            )

        # test with model overridden
        with mock.patch.object(test_models.HatWearer, model_method) as o:
            o.return_value = "model result"
            kwargs = {
                "model": test_models.HatWearer,
                attribute: "some override"
            }
            opal_wrapper = OpalRecordWrapper(**kwargs)
            self.assertEqual(
                getattr(opal_wrapper, method)(),
                "some override"
            )

    def test_get_api_name(self):
        self.get_tests("get_api_name", "api_name", "get_api_name")

    def test_get_display_name(self):
        self.get_tests("get_display_name", "display_name", "get_display_name")

    def test_get_icon(self):
        self.get_tests("get_icon", "icon", "get_icon")

    def get_get_template(self):
        self.get_tests("get_template", "template", "get_display_template")

    def test_is_singleton_class_arg(self):
        opal_wrapper = self.get_with_class_attrs(is_singleton=True)()
        self.assertTrue(
            opal_wrapper.is_singleton
        )
        self.assertTrue(
            opal_wrapper.singleton()
        )

    def test_is_singleton_args_override(self):
        opal_wrapper_cls = self.get_with_class_attrs(is_singleton=True)
        opal_wrapper = opal_wrapper_cls(is_singleton=False)
        self.assertFalse(
            opal_wrapper.is_singleton
        )
        self.assertFalse(
            opal_wrapper.singleton()
        )

    def test_is_singleton_model(self):
        opal_wrapper = OpalRecordWrapper(model=test_models.HatWearer)
        self.assertFalse(
            opal_wrapper.is_singleton
        )
        self.assertFalse(
            opal_wrapper.singleton()
        )

    def test_is_singleton_override_model(self):
        opal_wrapper = OpalRecordWrapper(
            model=test_models.HatWearer, is_singleton=True
        )
        self.assertTrue(
            opal_wrapper.is_singleton
        )
        self.assertTrue(
            opal_wrapper.singleton()
        )

    def test_is_singleton_model_without_attribute(self):
        opal_wrapper = OpalRecordWrapper(
            model=opal_models.Episode
        )

        self.assertIsNone(opal_wrapper.is_singleton)
        self.assertFalse(opal_wrapper.singleton())
