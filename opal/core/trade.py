"""
Utilities for import/export of patients and episodes
"""
import collections

from opal import models
from opal.core import subrecords

"""
Utilities
"""
def remove_key(d, key):
    """
    Remove the given key from the given dictionary recursively
    """
    for k, v in d.iteritems():
        if k == key:
            continue

        if isinstance(v, collections.Mapping):
            yield k, dict(remove_key(v, key))
        elif isinstance(v, list):
            yield k, [dict(remove_key(x, key)) for x in v]
        else:
            yield k, v


"""
Imports
"""

def match_or_create_patient(demographic, user):
    """
    Get a Patient record using demographics data

    Attempt the lookup using three methods:
        1. NHS Number
        2. DoB, First name, & Surname
        3. Create a new Demographic record
    """
    Demographics = subrecords.get_subrecord_from_model_name('Demographics')
    nhs_number = demographic.get('nhs_number')
    if nhs_number:
        try:
            return Demographics.objects.get(nhs_number=nhs_number).patient
        except Demographics.DoesNotExist:
            pass

    dob = demographic.get('date_of_birth')
    first_name = demographic.get('first_name')
    surname = demographic.get('surname')

    if all([dob, first_name, surname]):
        date_of_birth = datetime.strptime(dob, "%d/%m/%Y").date()
        try:
            return Demographics.objects.get(
                date_of_birth=date_of_birth,
                first_name=first_name,
                surname=surname,
            ).patient
        except Demographics.DoesNotExist:
            pass

    # Remove data we don't want to save
    if 'id' in demographic:
        del demographic['id']

    patient = models.Patient.objects.create()
    d = Demographics(patient=patient)
    d.update_from_dict(demographic, user)
    return patient

def import_patient(data, user=None):
    """
    Given a datastructure representing a Patient, import that patient.

    If required, pass in the user as a kwarg.

    1. Match or create the patient
    2. Iterate through episodes in the patient data, creating them as required
    """
    patient = match_or_create_patient(
        data['demographics'][0],
        user,
    )
    episodes = data.pop('episodes')

    patient.update_from_dict(data, user)
    return


"""
Exports
"""

def patient_id_to_json(patient_id, user=None):
    """
    Given a PATIENT_ID return the JSON export of that patient and the
    patient as a tuple:

    return (DATA, PATIENT)

    If requried, pass in the active user as a kwarg.

    If the patient does not exist, raise Patient.DoesNotExist.
    """
    patient = models.Patient.objects.get(pk=patient_id)

    data = patient.to_dict(user)

    # Active episode is not a concept which makes sense for a second system
    del data['active_episode_id']

    # Remove all "id" keys from the data
    data = dict(remove_key(data, 'id'))

    return data, patient
