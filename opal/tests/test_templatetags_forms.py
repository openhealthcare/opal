"""
Tests for our modal/form helpers
"""
from django.template import Template, Context
from django.test import TestCase

from opal.templatetags.forms import input, select, textarea

class TextareaTest(TestCase):
    def setUp(self):
        self.template = Template('{% load forms %}{% textarea label="hai" model="bai"%}')

    def test_textarea(self):
        rendered = self.template.render(Context({}))
        self.assertIn('ng-model="bai"', rendered)
        self.assertIn('hai', rendered)


class SelectTest(TestCase):
    def setUp(self):
        self.template = Template('{% load forms %}{% select label="hai" model="bai"%}')

    def test_select(self):
        rendered = self.template.render(Context({}))
        self.assertIn('ng-model="bai"', rendered)

        # remove white space
        cleaned = "".join([i.strip() for i in rendered.split("\n") if i.strip()])
        self.assertIn('<label class="control-label col-sm-3">hai</label>', cleaned)


class InputTest(TestCase):
    def setUp(self):
        self.template = Template('{% load forms %}{% input label="hai" model="bai"%}')

    def test_input(self):
        rendered = self.template.render(Context({}))
        self.assertIn('ng-model="bai"', rendered)
        self.assertIn('hai', rendered)
