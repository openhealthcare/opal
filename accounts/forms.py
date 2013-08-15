"""
Custom forms for user accounts
"""
from django.contrib.auth.forms import AdminPasswordChangeForm

class ChangePasswordForm(AdminPasswordChangeForm):
    """
    Set the profile force password flag to false.
    """
    def save(self, commit=True):
        super(ChangePasswordForm, self).save(commit=commit)
        profile = self.user.get_profile()
        profile.force_password_change = False
        profile.save()
        return self.user
