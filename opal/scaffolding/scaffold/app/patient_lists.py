"""
Defining OPAL PatientLists
"""
from opal import core, models

class AllPatientsList(core.patient_lists.PatientList):
    display_name = 'All Patients'

    def get_queryset(self):
        return models.Episode.objects.all()
