"""
Export something - a commandline utility
"""
import json

from django.core.management.base import BaseCommand

from opal.core import trade, views
from opal.models import Patient, Episode


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
        parser.add_argument(
            '--episode',
            dest='episode',
            help="ID of the episode you would like to export",
            default=None
        )

    def _export_patient(self, patient_id, options):
        try:
            excludes = options.get('exclude', '').split(',')
            data, patient = trade.patient_id_to_json(
                patient_id, excludes=excludes
            )
            return data
        except Patient.DoesNotExist:
            msg = 'Cannot find Patient with ID: {}'.format(patient_id)
            raise LookupError(msg)

    def _export_episode(self, patient_id, options):
        try:
            excludes = options.get('exclude', '').split(',')
            data, patient = trade.episode_id_to_json(
                patient_id, excludes=excludes
            )
            return data
        except Episode.DoesNotExist:
            msg = 'Cannot find Episode with ID: {}'.format(patient_id)
            raise LookupError(msg)


    def handle(self, *args, **options):
        """
        Commandline entrypoint
        """
        patient_id = options.get('patient', None)
        episode_id = options.get('episode', None)

        if not patient_id:
            if not episode_id:
                msg = 'What do you want to export? '\
                      'Try using the --patient or --episode argument'
                raise ValueError(msg)

        if patient_id:
            data = self._export_patient(patient_id, options)
        else:
            data = self._export_episode(episode_id, options)

        self.stdout.write(json.dumps(data, indent=2, cls=views.OpalSerializer))
