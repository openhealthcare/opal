"""
Unittests for opal.forms
"""
from mock import MagicMock, patch

from opal.core.test import OpalTestCase

from opal import forms

class ChangePasswordFormTestCase(OpalTestCase):
    def test_clean_password(self):
        f = forms.ChangePasswordForm(MagicMock(name='User'))
        f.cleaned_data = {'password1': 'some valid password'}
        p = f.clean_password1()
        self.assertEqual('some valid password', p)

    def test_short_password(self):
        f = forms.ChangePasswordForm(MagicMock(name='User'))
        f.cleaned_data = {'password1': 'some'}
        with self.assertRaises(forms.ValidationError):
            p = f.clean_password1()

    def test_banned_password(self):
        f = forms.ChangePasswordForm(MagicMock(name='User'))
        f.cleaned_data = {'password1': 'password'}
        with self.assertRaises(forms.ValidationError):
            p = f.clean_password1()
