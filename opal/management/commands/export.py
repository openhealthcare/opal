"""
Export something
"""
import json

from django.core.management.base import BaseCommand

from opal.core import trade, views
from opal.models import Patient


class Command(BaseCommand):
    """
    manage.py export --patient 34223

    Serialize a patient to JSON suitable for export/import.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--patient',
            dest='patient',
            help='ID of the patient you would like to export',
            default=None
        )

    def handle(self, *args, **options):
        """
        Commandline entrypoint
        """
        patient_id = options.get('patient', None)
        if not patient_id:
            raise ValueError('What do you want to export?')

        try:
            data, patient = trade.patient_id_to_json(patient_id)
        except Patient.DoesNotExist:
            msg = 'Cannot find Patient with ID: {}'.format(patient_id)
            raise ValueError(msg)
        print(json.dumps(data, indent=2, cls=views.OpalSerializer))
