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
    code          = models.CharField(max_length=255, blank=True, null=True)
    # We don't particularly use this in the current implementation, but we
    # include it in the model for the sake of FHIR CodeableConcept compatibility
    version       = models.CharField(max_length=255, blank=True, null=True)
