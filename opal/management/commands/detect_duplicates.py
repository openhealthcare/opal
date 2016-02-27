"""
Detect duplicates or suspiciously similar patients
"""
from django.core.management.base import BaseCommand

from opal.models import Patient, Episode

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Duplicate detection starting...")
        demographics = Patient.objects.all()[0].demographics_set.get().__class__.objects.all()
        patients = Patient.objects.count()
        suspicious = []
        suspicious_ids = {}

        for i, patient in enumerate(Patient.objects.all()):
            progress = '({0}% - {1} found)'.format(int(float(i+1)/patients*100), len(suspicious))
            patient_demographics = patient.demographics_set.get()
            name = patient_demographics.name
            self.stdout.write('{0} Examining {1}'.format(progress, name))

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
                if d.name == patient_demographics.name:
                    add_to_suspicious(d.patient, patient)
                if d.hospital_number == patient_demographics.hospital_number:
                    add_to_suspicious(d.patient, patient)
                if d.date_of_birth:
                    if patient_demographics.date_of_birth:
                        if d.date_of_birth == patient_demographics.date_of_birth:
                            add_to_suspicious(d.patient, patient)

        self.stdout.write("X" * 80)
        self.stdout.write("Detection sweep finished")
        self.stdout.write("X" * 80)

        for pair in suspicious:
            self.stdout.write("Suspicious Pair:")

            msg = '{0} {1}'.format(
                pair[0].demographics_set.get().name, pair[0].id
            )
            self.stdout.write(msg)

            msg = '{0} {1}'.format(
                pair[1].demographics_set.get().name, pair[1].id
            )
            self.stdout.write(msg)

        return
