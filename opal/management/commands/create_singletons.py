"""
Create singletons that may have been dropped
"""
import logging
from django.core.management.base import BaseCommand

from opal.models import Patient, Episode
from opal.core.subrecords import patient_subrecords, episode_subrecords


class Command(BaseCommand):

    def handle(self, *args, **options):
        logging.info("Creating Singletons")

        for patient in Patient.objects.all():
            logging.info('Examining {0}'.format(patient))
            for subclass in patient_subrecords():
                if subclass._is_singleton:
                    if subclass.objects.filter(patient=patient).count() == 0:
                        logging.info('Creating {0}'.format(subclass))
                        subclass.objects.create(patient=patient)

        for episode in Episode.objects.all():
            logging.info('Examining {0}'.format(episode))
            for subclass in episode_subrecords():
                if subclass._is_singleton:
                    if subclass.objects.filter(episode=episode).count() == 0:
                        logging.info('Creating {0}'.format(subclass))
                        subclass.objects.create(episode=episode)
        return
