"""
Custom forms for Opal!
"""
from django.forms import ValidationError
from django.contrib.auth.forms import AdminPasswordChangeForm

from opal.utils.banned_passwords import banned


class ChangePasswordForm(AdminPasswordChangeForm):
    """
    Set the profile force password flag to false.
    """
    MIN_LENGTH = 6

    def clean_password1(self):

        password1 = self.cleaned_data.get('password1')

        # At least MIN_LENGTH long
        if len(password1) < self.MIN_LENGTH:
            err = "The new password must be at least %d characters long."
            raise ValidationError(
                err % self.MIN_LENGTH
            )

        # Must not be a banned word
        if password1 in banned:
            raise ValidationError(
                "Sorry, %s is too common a password." % password1
            )

        return password1

    def save(self, commit=True):
        super(ChangePasswordForm, self).save(commit=commit)
        profile = self.user.profile
        profile.force_password_change = False
        profile.save()
        return self.user
