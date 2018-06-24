"""
Detect duplicates or suspiciously similar patients
"""
from django.core.management.base import BaseCommand

from opal.models import Patient


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Duplicate detection starting...")
        klass = Patient.objects.all()[0].demographics().__class__
        demographics = klass.objects.all()
        patients = Patient.objects.count()
        suspicious = []
        suspicious_ids = {}

        for i, patient in enumerate(Patient.objects.all()):
            progress = '({0}% - {1} found)'.format(
                int(float(i + 1) / patients * 100), len(suspicious)
            )
            patient_demographics = patient.demographics()
            self.stdout.write(
                '{0} Examining {1} {2}'.format(
                    progress,
                    patient_demographics.first_name,
                    patient_demographics.surname,
                )
            )

            def add_to_suspicious(patient, other_patient):
                if suspicious_ids.get(patient.id, False):
                    return
                if suspicious_ids.get(other_patient.id, False):
                    return

                suspicious.append([patient, other_patient])
                suspicious_ids[patient.id] = True
                suspicious_ids[other_patient.id] = True
                return

            for d in demographics:
                if d.patient.id == patient.id:
                    continue
                if d.surname == patient_demographics.surname:
                    if d.first_name == patient_demographics.first_name:
                        add_to_suspicious(d.patient, patient)
                if d.hospital_number == patient_demographics.hospital_number:
                    add_to_suspicious(d.patient, patient)
                if d.date_of_birth:
                    if patient_demographics.date_of_birth:
                        patient_dob = patient_demographics.date_of_birth
                        if d.date_of_birth == patient_dob:
                            add_to_suspicious(d.patient, patient)

        self.stdout.write("X" * 80)
        self.stdout.write("Detection sweep finished")
        self.stdout.write("X" * 80)

        for pair in suspicious:
            self.stdout.write("Suspicious Pair:")

            msg_1 = '{0} {1} {2}'.format(
                pair[0].demographics().first_name,
                pair[0].demographics().surname,
                pair[0].id
            )
            self.stdout.write(msg_1)

            msg_2 = '{0} {1} {2}'.format(
                pair[1].demographics().first_name,
                pair[1].demographics().surname,
                pair[1].id
            )
            self.stdout.write(msg_2)

        return
