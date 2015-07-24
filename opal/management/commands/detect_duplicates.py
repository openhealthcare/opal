"""
Detect duplicates or suspiciously similar patients
"""
from django.core.management.base import BaseCommand

from opal.models import Patient, Episode

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        print "Duplicate detection starting..."
        demographics = Patient.objects.all()[0].demographics_set.get().__class__.objects.all()
        patients = Patient.objects.count()
        suspicious = []
        suspicious_ids = {}

        for i, patient in enumerate(Patient.objects.all()):
            progress = '({0}% - {1} found)'.format(int(float(i+1)/patients*100), len(suspicious))
            patient_demographics = patient.demographics_set.get()
            name = patient_demographics.name
            print progress, 'Examining', name

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
            
        print "X" * 80
        print "Detection sweep finished"
        print "X" * 80

        for pair in suspicious:
            print "Suspicious Pair:"
            print pair[0].demographics_set.get().name, pair[0].episode_set.all()[0].id
            print pair[1].demographics_set.get().name, pair[1].episode_set.all()[0].id
            
        return
