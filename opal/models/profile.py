"""
OPAL models for users and their profile.
"""
from django.contrib.auth.models import User
from django.db import models

class Filter(models.Model):
    """
    Saved filters for users extracting data.
    """
    user     = models.ForeignKey(User)
    name     = models.CharField(max_length=200)
    criteria = models.TextField()
