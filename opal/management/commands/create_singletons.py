"""
Create singletons that may have been dropped
"""
import collections
import json
from optparse import make_option

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from opal.models import Patient, Episode, PatientSubrecord, EpisodeSubrecord

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        print "Creating Singletons"
        for patient in Patient.objects.all():
            print 'Examining', patient
            for subclass in PatientSubrecord.__subclasses__():
                if subclass._is_singleton:
                    if subclass.objects.filter(patient=patient).count() == 0:
                        print 'Creating', subclass
                        subclass.objects.create(patient=patient)
        for episode in Episode.objects.all():
            print 'Examining', episode
            for subclass in EpisodeSubrecord.__subclasses__():
                if subclass._is_singleton:
                    if subclass.objects.filter(episode=episode).count() == 0:
                        print 'Creating', subclass
                        subclass.objects.create(episode=episode)
        return
