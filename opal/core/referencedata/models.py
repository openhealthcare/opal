"""
Opal Referencedata models
"""
from django.db import models

class CodeableConcept(models.Model):
    """
    A codeable concept from an upstream terminology coding system
    """
    display       = models.CharField(max_length=255, blank=True, null=True)
    system        = models.CharField(max_length=255, blank=True, null=True)
    version       = models.CharField(max_length=255, blank=True, null=True)
    code          = models.CharField(max_length=255, blank=True, null=True)
