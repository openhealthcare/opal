from django.db import models

class Antimicrobial(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

class Destination(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name
