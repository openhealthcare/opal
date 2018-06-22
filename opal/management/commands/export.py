"""
Export something - a commandline utility
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
        parser.add_argument(
            '--exclude',
            dest='exclude',
            help='Comma separated list of subrecord api_names to exclude',
            default=""
        )

    def handle(self, *args, **options):
        """
        Commandline entrypoint
        """
        patient_id = options.get('patient', None)
        if not patient_id:
            msg = 'What do you want to export? '\
                  'Try using the --patient argument'
            raise ValueError(msg)
        try:
            excludes = options.get('exclude', '').split(',')
            data, patient = trade.patient_id_to_json(
                patient_id, excludes=excludes
            )
        except Patient.DoesNotExist:
            msg = 'Cannot find Patient with ID: {}'.format(patient_id)
            raise LookupError(msg)
        self.stdout.write(json.dumps(data, indent=2, cls=views.OpalSerializer))
