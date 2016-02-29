from opal.models import Patient
from django.db import models


class GlossolaliaSubscription(models.Model):
    SERIALISED_FIELDS = ["subscription_type", "gloss_id"]
    ALL_INFORMATION = "all_information"
    CORE_DEMOGRAPHICS = "core_demographics"
    SUBSCRIPTION_TYPES = (
        (ALL_INFORMATION, 'All Information'),
        (CORE_DEMOGRAPHICS, 'Core Demographics'),
    )
    patient = models.ForeignKey(Patient)
    subscription_type = models.CharField(
        max_length=2, choices=SUBSCRIPTION_TYPES, default=ALL_INFORMATION
    )
    gloss_id = models.IntegerField()
