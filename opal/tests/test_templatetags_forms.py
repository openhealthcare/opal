"""
Tests for our modal/form helpers
"""
import json
from unittest.mock import patch

from django.template import Template, Context
from django.test import TestCase

from opal.templatetags import forms
from opal.templatetags.forms import (
    process_steps, infer_from_subrecord_field_path, date_of_birth_field,
    extract_common_args
)
from opal.core.views import OpalSerializer


class TestGetStyleTestCase(TestCase):
    def test_defaults_to_horizontal(self):
        self.assertEqual('horizontal', forms.get_style({}))

    def test_can_override_with_vertical(self):
        self.assertEqual('vertical', forms.get_style({'style': 'vertical'}))

    def test_can_explicitly_pass_in_horizontal(self):
        self.assertEqual('horizontal', forms.get_style({'style':'horizontal'}))

    def test_only_specific_style_values_allowed(self):
        with self.assertRaises(ValueError):
            forms.get_style({'style': 'inverted'})


class TestInferFromSubrecordPath(TestCase):
    def test_infer_char_field(self):
        ctx = infer_from_subrecord_field_path("DogOwner.name")
        self.assertEqual(ctx["label"], "Name")
        self.assertTrue("lookuplist" not in ctx)
        self.assertEqual(ctx["model"], "editing.dog_owner.name")

    def test_infer_required_fields(self):
        ctx = infer_from_subrecord_field_path("DogOwner.name")
        self.assertTrue(ctx["required"])

    def test_infer_foreign_key_for_free_text(self):
        ctx = infer_from_subrecord_field_path("DogOwner.dog")
        self.assertEqual(ctx["label"], "Dog")
        self.assertEqual(ctx["model"], "editing.dog_owner.dog")
        self.assertEqual(ctx["lookuplist"], "dog_list")
        self.assertFalse(ctx["required"])

    def test_get_label_from_the_model(self):
        ctx = infer_from_subrecord_field_path("HatWearer.wearing_a_hat")
        self.assertEqual(ctx["label"], "Wearing A Hat")

    def test_infer_many_to_many_fields(self):
        ctx = infer_from_subrecord_field_path("HatWearer.hats")
        self.assertEqual(ctx["label"], "Hats")
        self.assertEqual(ctx["model"], "editing.hat_wearer.hats")
        self.assertEqual(ctx["lookuplist"], "hat_list")

    def test_infer_blank_fields(self):
        # at present we consider blank fields even if they are aren't nullable
        # to be not required
        ctx = infer_from_subrecord_field_path("Birthday.birth_date")
        self.assertFalse(ctx["required"])

    def test_infer_choice_fields_from_charfield(self):
        ctx = infer_from_subrecord_field_path("FavouriteColour.name")
        choices = json.loads(ctx["lookuplist"])
        self.assertEqual(choices, ["purple", "yellow", "blue"])

    @patch("opal.templatetags.forms.json")
    def test_infer_choice_fields_from_charfield_with_serialiser(self, js):
        js.dumps.return_value = '["purple", "yellow", "blue"]'
        ctx = infer_from_subrecord_field_path("FavouriteColour.name")
        choices = json.loads(ctx["lookuplist"])
        self.assertEqual(choices, ["purple", "yellow", "blue"])
        js.dumps.assert_called_once_with(
            ["purple", "yellow", "blue"],
            cls=OpalSerializer
        )

    def test_infer_element_name(self):
        ctx = infer_from_subrecord_field_path("Birthday.birth_date")
        self.assertEqual(
            ctx["element_name"],
            "editing.birthday._client.id + '_birth_date'"
        )

    def test_infer_element_type_number(self):
        ctx = infer_from_subrecord_field_path("FavouriteNumber.number")
        self.assertEqual(
            ctx["element_type"],
            "number"
        )

    def test_infer_element_type_text(self):
        ctx = infer_from_subrecord_field_path("HoundOwner.name")
        self.assertNotIn("element_type", ctx)


class ExtractCommonArgsTestCase(TestCase):
    def test_required_override(self):
        tag_kwargs = dict(field="Demographics.hospital_number", required=True)
        ctx = extract_common_args(tag_kwargs)
        self.assertTrue(ctx["required"])
        tag_kwargs = dict(field="Demographics.hospital_number", required=False)
        ctx = extract_common_args(tag_kwargs)
        self.assertFalse(ctx["required"])

    def test_visibility_show(self):
        show_kwargs = dict(show="yes", model="something")
        ctx = extract_common_args(show_kwargs)
        self.assertEqual(ctx['visibility'], ' ng-show="yes"')

    def test_visibility_hide(self):
        show_kwargs = dict(hide="yes", model="something")
        ctx = extract_common_args(show_kwargs)
        self.assertEqual(ctx['visibility'], 'ng-hide="yes"')

    def test_element_type(self):
        tag_kwargs = dict(field="FavouriteNumber.number", element_type="text")
        ctx = extract_common_args(tag_kwargs)
        self.assertEqual(ctx["element_type"], "text")


class TextareaTest(TestCase):
    def setUp(self):
        self.template = Template('{% load forms %}{% textarea label="hai" model="bai"%}')

    def test_textarea(self):
        rendered = self.template.render(Context({}))
        self.assertIn('ng-model="bai"', rendered)
        self.assertIn('hai', rendered)

    def test_element_name(self):
        tpl = Template('{% load forms %}{% textarea label="hai" model="bai" element_name="onions"%}')
        rendered = tpl.render(Context({}))
        self.assertIn('name="[[ onions ]]"', rendered)

    def test_change(self):
        tpl = Template('{% load forms %}{% textarea label="hai" change="doStuff" model="bai" element_name="onions"%}')
        rendered = tpl.render(Context({}))
        self.assertIn('ng-change="doStuff"', rendered)

    def test_rows(self):
        tpl = Template('{% load forms %}{% textarea label="hai" model="bai" rows=2 element_name="onions"%}')
        rendered = tpl.render(Context({}))
        self.assertIn('rows="2"', rendered)


class InputTest(TestCase):

    def test_load_from_model(self):
        tpl = Template('{% load forms %}{% input field="DogOwner.dog" %}')
        rendered = tpl.render(Context({}))
        self.assertIn("editing.dog_owner.dog", rendered)
        self.assertIn("dog_list", rendered)

    def test_element_type(self):
        tpl = Template(
            '{% load forms %}{% input field="FavouriteNumber.number" %}'
        )
        rendered = tpl.render(Context({}))
        self.assertIn('type="number"', rendered)

    def test_use_verbose_name_from_model(self):
        tpl = Template('{% load forms %}{% input field="HoundOwner.dog" %}')
        rendered = tpl.render(Context({}))
        self.assertIn("Hound", rendered)

    def test_override_from_model(self):
        tpl = Template('{% load forms %}{% input label="Cat" model="editing.cat_owner.cat" lookuplist="cat_list" field="DogOwner.dog" %}')
        rendered = tpl.render(Context({}))
        self.assertIn("editing.cat_owner.cat", rendered)
        self.assertIn("cat_list", rendered)
        self.assertIn("Cat", rendered)

    def test_input(self):
        template = Template('{% load forms %}{% input label="hai" model="bai"%}')
        rendered = template.render(Context({}))
        self.assertIn('ng-model="bai"', rendered)
        self.assertIn('hai', rendered)

    def test_max_length(self):
        tpl = Template('{% load forms %}{% input field="DogOwner.name" %}')
        rendered = tpl.render(Context({}))
        self.assertIn('ng-maxlength="200"', rendered)

    def test_hide(self):
        tpl = Template('{% load forms %}{% input label="hai" model="bai" hide="status=\'reloading\'"%}')
        self.assertIn('ng-hide="status=\'reloading\'"', tpl.render(Context({})))

    def test_show(self):
        tpl = Template('{% load forms %}{% input label="hai" model="bai" show="status=\'loaded\'"%}')
        self.assertIn('ng-show="status=\'loaded\'"', tpl.render(Context({})))

    def test_show_hide(self):
        tpl = Template('{% load forms %}{% input label="hai" model="bai" hide="status=\'reloading\'" show="status=\'loaded\'" %}')
        self.assertIn('ng-show="status=\'loaded\'"', tpl.render(Context({})))
        self.assertIn('ng-hide="status=\'reloading\'"', tpl.render(Context({})))

    def test_fa_icon(self):
        tpl = Template('{% load forms %}{% input label="hai" model="bai" icon="fa-eye"%}')
        self.assertIn('<i class="fa fa-eye"></i>', tpl.render(Context({})))

    def test_glyph_icon(self):
        tpl = Template('{% load forms %}{% input label="hai" model="bai" icon="glyphicon-boat"%}')
        self.assertIn('<i class="glyphicon glyphicon-boat"></i>', tpl.render(Context({})))

    def test_unknown_icon(self):
        tpl = Template('{% load forms %}{% input label="hai" model="bai" icon="myicon"%}')
        self.assertIn('<i class="myicon"></i>', tpl.render(Context({})))

    def test_disabled(self):
        tpl = Template('{% load forms %}{% input label="hai" model="bai" disabled="status=\'reloading\'"%}')
        self.assertIn('ng-disabled="status=\'reloading\'"', tpl.render(Context({})))

    def test_model_name(self):
        tpl = Template('{% load forms %}{% input label="hai" model="bai[0].something" %}')
        self.assertIn('bai0_something', tpl.render(Context({})))

    def test_element_name(self):
        tpl = Template('{% load forms %}{% input label="hai" model="bai" element_name="onions"%}')
        rendered = tpl.render(Context({}))
        self.assertIn('name="[[ onions ]]"', rendered)

    def test_max_length_error(self):
        tpl = Template('{% load forms %}{% input label="hai" model="bai" element_name="onions" maxlength="50" %}')
        rendered = tpl.render(Context({}))
        self.assertIn('"(form.$submitted || form[onions].$invalid) && form[onions].$error.maxlength', rendered)

    def test_required_error(self):
        tpl = Template('{% load forms %}{% input label="hai" model="bai" element_name="onions" required=True %}')
        rendered = tpl.render(Context({}))
        self.assertIn('(form[onions].$dirty || form.$submitted) && form[onions].$error.required', rendered)

    def test_change(self):
        tpl = Template('{% load forms %}{% input label="hai" change="doStuff" model="bai" element_name="onions"%}')
        rendered = tpl.render(Context({}))
        self.assertIn('ng-change="doStuff"', rendered)


class CheckboxTestCase(TestCase):

    def test_checkbox(self):
        template = Template('{% load forms %}{% checkbox label="hai" model="bai"%}')
        rendered = template.render(Context({}))
        self.assertIn('ng-model="bai"', rendered)
        self.assertIn('hai', rendered)

    def test_element_name(self):
        tpl = Template('{% load forms %}{% checkbox label="hai" model="bai" element_name="onions"%}')
        rendered = tpl.render(Context({}))
        self.assertIn('name="[[ onions ]]"', rendered)

    def test_set_element_id(self):
        tpl = Template('{% load forms %}{% checkbox label="hai" model="bai" element_name="onions"%}')
        rendered = tpl.render(Context({}))
        self.assertIn('id="checkbox_[[ onions ]]"', rendered)

    def test_change(self):
        tpl = Template('{% load forms %}{% checkbox label="hai" change="doStuff" model="bai" element_name="onions"%}')
        rendered = tpl.render(Context({}))
        self.assertIn('ng-change="doStuff"', rendered)


class TimepickerTestCase(TestCase):
    def test_visibility(self):
        template = Template('{% load forms %}{% timepicker show="someVar" field="Dinner.time" %}')
        rendered = template.render(Context({}))
        self.assertIn('ng-show="someVar"', rendered)

    def test_change(self):
        template = Template('{% load forms %}{% timepicker change="someVar()" field="Dinner.time" %}')
        rendered = template.render(Context({}))
        self.assertIn('change="someVar()"', rendered)

    def test_model(self):
        template = Template('{% load forms %}{% timepicker model="trees" field="Dinner.time" %}')
        rendered = template.render(Context({}))
        self.assertIn('trees', rendered)

    def test_label(self):
        template = Template('{% load forms %}{% timepicker label="trees" field="Dinner.time" %}')
        rendered = template.render(Context({}))
        self.assertIn('trees', rendered)


class DatepickerTestCase(TestCase):

    def test_datepicker(self):
        template = Template('{% load forms %}{% datepicker label="hai" model="bai" mindate="Date(2013, 12, 22)" %}')
        rendered = template.render(Context({}))
        self.assertIn('ng-model="bai"', rendered)
        self.assertIn('hai', rendered)

    def test_datepicker_options_default(self):
        template = Template('{% load forms %}{% datepicker label="hai" model="bai" mindate="Date(2013, 12, 22)" %}')
        rendered = template.render(Context({}))
        self.assertNotIn('bai = now', rendered)

    def test_datepicker_options_on(self):
        template = Template('{% load forms %}{% datepicker label="hai" model="bai" mindate="Date(2013, 12, 22)" user_options=True %}')
        rendered = template.render(Context({}))
        self.assertIn('bai = dateHelper.now()', rendered)

    def test_datepicker_min_date(self):
        template = Template('{% load forms %}{% datepicker label="hai" model="bai" mindate="Date(2013, 12, 22)" %}')
        rendered = template.render(Context({}))
        self.assertIn('min-date="Date(2013, 12, 22)"', rendered)

    def test_element_name(self):
        tpl = Template('{% load forms %}{% datepicker label="hai" model="bai" element_name="onions"%}')
        rendered = tpl.render(Context({}))
        self.assertIn('name="[[ onions ]]"', rendered)

    def test_is_open(self):
        tpl = Template('{% load forms %}{% datepicker label="hai" model="bai" element_name="onions"%}')
        rendered = tpl.render(Context({}))
        self.assertIn('is-open="form[onions + \'_open\']', rendered)
        self.assertIn('ng-focus="form[onions + \'_open\']=true"', rendered)

    def test_hide(self):
        tpl = Template(
            '{% load forms %}{% datepicker label="hai" model="bai" hide="onions"%}'
        )
        rendered = tpl.render(Context({}))
        self.assertIn('ng-hide="onions"', rendered)

    def test_show(self):
        tpl = Template(
            '{% load forms %}{% datepicker label="hai" model="bai" hide="onions"%}'
        )
        rendered = tpl.render(Context({}))
        self.assertIn('ng-hide="onions"', rendered)

    def test_change(self):
        tpl = Template('{% load forms %}{% datepicker label="hai" change="doStuff" model="bai" element_name="onions"%}')
        rendered = tpl.render(Context({}))
        self.assertIn('ng-change="doStuff"', rendered)

    def test_required_error(self):
        tpl = Template('{% load forms %}{% datepicker label="hai" model="bai" element_name="onions" required=True %}')
        rendered = tpl.render(Context({}))
        self.assertIn('(form[onions].$dirty || form.$submitted) && form[onions].$error.required', rendered)


class DateTimePickerTestCase(TestCase):
    def test_generic(self):
        template = Template('{% load forms %}{% datetimepicker field="Colour.name" %}')
        rendered = template.render(Context({}))
        self.assertEqual(rendered.count('editing.colour.name'), 2)

    def test_label_date(self):
        template = Template('{% load forms %}{% datetimepicker field="Colour.name" date_label="something" %}')
        rendered = template.render(Context({}))
        self.assertIn('something', rendered)

    def test_label_time(self):
        template = Template('{% load forms %}{% datetimepicker field="Colour.name" time_label="something" %}')
        rendered = template.render(Context({}))
        self.assertIn('something', rendered)

    def test_change(self):
        template = Template('{% load forms %}{% datetimepicker field="Colour.name" change="something()" %}')
        rendered = template.render(Context({}))
        self.assertEqual(rendered.count("something()"), 2)

    def test_hide(self):
        tpl = Template(
            '{% load forms %}{% datetimepicker label="hai" model="bai" hide="onions"%}'
        )
        rendered = tpl.render(Context({}))
        self.assertIn('ng-hide="onions"', rendered)

    def test_show(self):
        tpl = Template(
            '{% load forms %}{% datetimepicker label="hai" model="bai" hide="onions"%}'
        )
        rendered = tpl.render(Context({}))
        self.assertIn('ng-hide="onions"', rendered)


@patch("opal.templatetags.forms.extract_common_args")
class RadioArgExractTestCase(TestCase):
    def test_radio_lookuplists(self, extract_common_args):
        extract_common_args.return_value = {}
        result = forms._radio(lookuplist="something")
        self.assertEqual(
            result, dict(lookuplist="something")
        )

    def test_extract_common_args(self, extract_common_args):
        extract_common_args.return_value = {"something": "else"}
        self.assertEqual(
            forms._radio(),
            {"something": "else", "lookuplist": None}
        )


class RadioVerticalTestCase(TestCase):
    def test_radio(self):
        template = Template('{% load forms %}{% radio_vertical label="hai" model="bai"%}')
        rendered = template.render(Context({}))
        self.assertIn('ng-model="bai"', rendered)
        self.assertIn('hai', rendered)

    def test_radio_lookuplists(self):
        template = Template('{% load forms %}{% radio_vertical field="FavouriteColour.name" lookuplist="[\'rainbow\']" %}')
        rendered = template.render(Context({}))
        self.assertIn('rainbow', rendered)
        # make sure we're overwriting the existing choice field
        self.assertNotIn('purple', rendered)

    def test_radio_infer_lookuplists(self):
        template = Template('{% load forms %}{% radio_vertical field="FavouriteColour.name" %}')
        rendered = template.render(Context({}))
        self.assertIn('purple', rendered)

    def test_element_name(self):
        tpl = Template('{% load forms %}{% radio_vertical label="hai" model="bai" element_name="onions"%}')
        rendered = tpl.render(Context({}))
        self.assertIn('name="[[ onions ]]"', rendered)

    def test_element_name_required(self):
        tpl = Template('{% load forms %}{% radio_vertical label="hai" model="bai" element_name="onions" required=True %}')
        rendered = tpl.render(Context({}))
        self.assertIn('form.$submitted && form[onions].$error.required"', rendered)

    def test_change(self):
        tpl = Template('{% load forms %}{% radio_vertical label="hai" change="doStuff" model="bai" element_name="onions"%}')
        rendered = tpl.render(Context({}))
        self.assertIn('ng-change="doStuff"', rendered)


class RadioTestCase(TestCase):

    def test_radio(self):
        template = Template('{% load forms %}{% radio label="hai" model="bai"%}')
        rendered = template.render(Context({}))
        self.assertIn('ng-model="bai"', rendered)
        self.assertIn('hai', rendered)

    def test_radio_lookuplists(self):
        template = Template('{% load forms %}{% radio field="FavouriteColour.name" lookuplist="[\'rainbow\']" %}')
        rendered = template.render(Context({}))
        self.assertIn('rainbow', rendered)
        # make sure we're overwriting the existing choice field
        self.assertNotIn('purple', rendered)

    def test_radio_infer_lookuplists(self):
        template = Template('{% load forms %}{% radio field="FavouriteColour.name" %}')
        rendered = template.render(Context({}))
        self.assertIn('purple', rendered)

    def test_element_name(self):
        tpl = Template('{% load forms %}{% radio label="hai" model="bai" element_name="onions"%}')
        rendered = tpl.render(Context({}))
        self.assertIn('name="[[ onions ]]"', rendered)

    def test_element_name_required(self):
        tpl = Template('{% load forms %}{% radio label="hai" model="bai" element_name="onions" required=True %}')
        rendered = tpl.render(Context({}))
        self.assertIn('form.$submitted && form[onions].$error.required"', rendered)

    def test_change(self):
        tpl = Template('{% load forms %}{% radio label="hai" change="doStuff" model="bai" element_name="onions"%}')
        rendered = tpl.render(Context({}))
        self.assertIn('ng-change="doStuff"', rendered)


class SelectTestCase(TestCase):

    def test_select(self):
        template = Template('{% load forms %}{% select label="hai" model="bai" %}')
        rendered = template.render(Context({}))
        self.assertIn('ng-model="bai"', rendered)

        # remove white space
        cleaned = "".join([i.strip() for i in rendered.split("\n") if i.strip()])
        self.assertIn('<label class="control-label col-sm-3">hai</label>', cleaned)

    def test_select_lookuplist(self):
        template = Template('{% load forms %}{% select label="hai" model="bai" lookuplist="[1,2,3]" %}')
        rendered = template.render(Context({}))
        self.assertIn('ng-model="bai"', rendered)

        # remove white space
        cleaned = "".join([i.strip() for i in rendered.split("\n") if i.strip()])
        self.assertIn('<label class="control-label col-sm-3">hai</label>', cleaned)

    def test_help_text(self):
        template = Template('{% load forms %}{% select label="hai" model="bai" lookuplist="[1,2,3]" help_text="informative help text" %}')
        rendered = template.render(Context({}))
        self.assertIn('informative help text', rendered)

    def test_load_from_model(self):
        tpl = Template('{% load forms %}{% select field="DogOwner.dog" %}')
        rendered = tpl.render(Context({}))
        self.assertIn("editing.dog_owner.dog", rendered)
        self.assertIn("dog_list", rendered)

    def test_override_from_model(self):
        tpl = Template('{% load forms %}{% select label="Cat" model="editing.cat_owner.cat" lookuplist="cat_list" field="DogOwner.dog" %}')
        rendered = tpl.render(Context({}))
        self.assertIn("editing.cat_owner.cat", rendered)
        self.assertIn("cat_list", rendered)
        self.assertIn("Cat", rendered)

    def test_element_name(self):
        tpl = Template('{% load forms %}{% select label="hai" model="bai" element_name="onions"%}')
        rendered = tpl.render(Context({}))
        self.assertIn('name="[[ onions ]]"', rendered)

    def test_element_name_required(self):
        tpl = Template('{% load forms %}{% select label="hai" model="bai" element_name="onions" required=True %}')
        rendered = tpl.render(Context({}))
        self.assertIn('"form.$submitted && form[onions].$error.required"', rendered)

    def test_change(self):
        tpl = Template('{% load forms %}{% select label="hai" change="doStuff" model="bai" element_name="onions"%}')
        rendered = tpl.render(Context({}))
        self.assertIn('ng-change="doStuff"', rendered)


class StaticTestCase(TestCase):

    def test_static(self):
        tpl = Template('{% load forms %}{% static "DogOwner.name" %}')
        rendered = tpl.render(Context({}))
        self.assertIn('editing.dog_owner.name', rendered)

    def test_date(self):
        tpl = Template('{% load forms %}{% static "Demographics.date_of_birth" %}')
        rendered = tpl.render(Context({}))
        self.assertIn('editing.demographics.date_of_birth', rendered)
        self.assertIn('displayDate', rendered)


class IconTestCase(TestCase):

    def test_fa_icon(self):
        tpl = Template('{% load forms %}{% icon "fa-eye" %}')
        self.assertIn('<i class="fa fa-eye"></i>', tpl.render(Context({})))

    def test_glyph_icon(self):
        tpl = Template('{% load forms %}{% icon "glyphicon-boat" %}')
        self.assertIn('<i class="glyphicon glyphicon-boat"></i>', tpl.render(Context({})))

    def test_form_some_random_user_string_482(self):
        # Regression test for https://github.com/opal/issues/482
        tpl = Template('{% load forms %}{% icon "this-is-my-icon-shut-up-opal" %}')
        self.assertIn('<i class="this-is-my-icon-shut-up-opal"></i>', tpl.render(Context({})))


class ProcessStepsTestCase(TestCase):

    def test_process_steps(self):
        ctx = process_steps(
            process_steps=1,
            complete=False,
            disabled=False,
            active=True,
            show_titles=True
        )
        expected = dict(
            process_steps=1,
            complete=False,
            disabled=False,
            active=True,
            show_index=False,
            show_titles=True
        )
        self.assertEqual(expected, ctx)


class DateOfBirthTestCase(TestCase):
    def test_set_field(self):
        ctx = date_of_birth_field(model_name="something")
        expected = dict(
            style="horizontal",
            model_name="something"
        )
        self.assertEqual(expected, ctx)

    def test_default(self):
        ctx = date_of_birth_field()
        expected = dict(
            model_name="editing.demographics.date_of_birth",
            style='horizontal'
        )
        self.assertEqual(expected, ctx)

    def test_render(self):
        tpl = Template('{% load forms %}{% date_of_birth_field %}')
        rendered = tpl.render(Context({}))
        self.assertIn("editing.demographics.date_of_birth", rendered)
