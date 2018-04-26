"""
Load something - a commandline utility
"""
import json

from django.core.management.base import BaseCommand

from opal.core import trade
from opal.models import Patient
from opal.utils import write


class Command(BaseCommand):
    """
    manage.py load --patient path/to/file.json

    Import a patient from a JSON file
    """
    def add_arguments(self, parser):
        parser.add_argument(
            '--patient', '-p',
            dest='patient_file',
            help='Path to file containing a patient',
            default=None
        )

    def handle(self, *args, **options):
        """
        Commandline entrypoint
        """
        patient_file = options.get('patient_file', None)
        if patient_file is None:
            raise ValueError('What do you want to import ? Try using the --patient argument')

        with open(patient_file, 'r') as fh:
            data = json.loads(fh.read())
            write('Read patient data file, beginning import process.')
            trade.import_patient(data)
