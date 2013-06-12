# These are models for testing.
# TODO move these to tests directory so they are not made available when app is
# added to INSTALLED_APPS.

from django.db import models
from utils.fields import ForeignKeyOrFreeText

class Colour(models.Model):
    name = models.CharField(max_length=255)

class Person(models.Model):
    favorite_colour = ForeignKeyOrFreeText(Colour)
