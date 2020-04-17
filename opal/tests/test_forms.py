"""
Unittests for opal.forms
"""
from unittest.mock import MagicMock, patch

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

    def test_save(self):
        self.user.profile.force_password_change = True
        self.user.profile.save()
        self.assertEqual(True, self.user.profile.force_password_change)
        data = {
            'old_password' : 'password',
            'password1': 'abc123HHHH',
            'password2': 'abc123HHHH'
        }
        f = forms.ChangePasswordForm(self.user, data)
        self.assertTrue(f.is_valid())
        user = f.save()
        self.assertEqual(False, user.profile.force_password_change)
