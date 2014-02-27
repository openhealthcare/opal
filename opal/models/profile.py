"""
OPAL models for users and their profile.
"""
from django.contrib.auth.models import User
from django.db import models

# class UserProfile(models.Model):
#     """
#     Profile for our user
#     """
#     user                  = models.ForeignKey(User, unique=True)
#     force_password_change = models.BooleanField(default=True)
#     can_extract           = models.BooleanField(default=False)
#     readonly              = models.BooleanField(default=False)


class Filter(models.Model):
    """
    Saved filters for users extracting data.
    """
    user     = models.ForeignKey(User)
    name     = models.CharField(max_length=200)
    criteria = models.TextField()
