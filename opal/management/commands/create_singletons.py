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

        for subclass in patient_subrecords():
            if subclass._is_singleton:
                to_create = []
                related_name = subclass.__name__.lower()
                patients_to_be_updated = Patient.objects.filter(
                    **{related_name: None}
                )
                for patient in patients_to_be_updated:
                    logging.info('Creating {0}'.format(subclass))
                    to_create.append(subclass(patient=patient))
                subclass.objects.bulk_create(to_create)

        for subclass in episode_subrecords():
            if subclass._is_singleton:
                to_create = []
                related_name = subclass.__name__.lower()
                episodes_to_be_updated = Episode.objects.filter(
                    **{related_name: None}
                )
                for episode in episodes_to_be_updated:
                    logging.info('Creating {0}'.format(subclass))
                    to_create.append(subclass(episode=episode))
                subclass.objects.bulk_create(to_create)

        return
