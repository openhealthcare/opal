"""
Models to allow us custom attributes related to users.
"""
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Profile for our user
    """
    user                  = models.ForeignKey(User, unique=True)
    force_password_change = models.BooleanField(default=True)
