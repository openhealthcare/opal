"""
Connect profile signals
"""
from django.contrib.auth.models import User
from django.db.models import signals

from accounts.models import UserProfile

def force_password_change_on_frist_login(sender, instance, created, raw,
                                         using, update_fields):
    """
    If this is a new User, force a password change when they first login.
    """
    if not created:
        return
    UserProfile.objects.create(user=instance, force_password_change=True)

signals.post_save.connect(force_password_change_on_frist_login, sender=User,
                          dispatch_uid='accounts.models')
