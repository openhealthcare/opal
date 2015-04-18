"""
Models for just our tests
"""
from django.db import models as dmodels
from opal import models

class Colour(models.EpisodeSubrecord):
    name = dmodels.CharField(max_length=200)

