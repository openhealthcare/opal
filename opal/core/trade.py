"""
Utilities for import/export of patients and episodes
"""
import collections
import copy
import datetime
import imp
import sys
import types

from django.db import transaction

from opal import models
from opal.core import subrecords



"""
Utilities
"""


def _remove_key(d, key):
    """
    Remove the given key from the given dictionary recursively
    """
    for k, v in d.iteritems():
        if k == key:
            continue

        if isinstance(v, collections.Mapping):
            yield k, dict(_remove_key(v, key))
        elif isinstance(v, list):
            yield k, [dict(_remove_key(x, key)) for x in v]
        else:
            yield k, v

def remove_keys(d, *keys):
    """
    Recursively remove many keys from a dictionary
    """
    if len(keys) == 0:
        return d
    if len(keys) == 1:
        return dict(_remove_key(d, keys[0]))
    return remove_keys(dict(remove_keys(d, keys[0])), *keys[1:])


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
        except (Demographics.DoesNotExist, models.Patient.DoesNotExist):
            pass

    dob        = demographic.get('date_of_birth')
    first_name = demographic.get('first_name')
    surname    = demographic.get('surname')

    if all([dob, first_name, surname]):
        date_of_birth = datetime.datetime.strptime(dob, "%d/%m/%Y").date()
        try:
            return Demographics.objects.get(
                date_of_birth=date_of_birth,
                first_name=first_name,
                surname=surname,
            ).patient
        except (Demographics.DoesNotExist, models.Patient.DoesNotExist):
            pass

    patient = models.Patient.objects.create()
    patient.demographics_set.get().update_from_dict(demographic, user)
    return patient


def import_patient_subrecord_data(api_name, data, patient, user=None):
    """
    Given the API_NAME of a patient subrecord, some DATA containing n
    instances of that subrecord, and a patient, save that data to the
    patient.

    If required, pass in the user as a kwarg
    """
    subrecord = subrecords.get_subrecord_from_api_name(api_name)
    return subrecord.bulk_update_from_dicts(patient, data, user)


def create_episode_for_patient(patient, episode_data, user=None):
    """
    Given a PATIENT, some EPISODE_DATA and maybe a USER, create
    that episode.
    """
    episode_fields = models.Episode._get_fieldnames_to_serialize()
    episode_dict = {}
    episode_subrecords = {}

    for key, value in episode_data.items():
        if key in episode_fields:
            episode_dict[key] = value
        else:
            episode_subrecords[key] = value

    episode = patient.create_episode()
    episode.update_from_dict(episode_dict, user)

    patient.bulk_update(episode_subrecords, user, episode=episode)


@transaction.atomic
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

    for episode in episodes.values():
        create_episode_for_patient(patient, episode, user=user)

    for key, value in data.items():
        if key == 'demographics':
            continue  # We already did that one.
        import_patient_subrecord_data(key, value, patient, user=user)

    return


"""
Exports
"""

def patient_id_to_json(patient_id, user=None, exclude=None):
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

    # Remove all "id", and consistency data
    data = remove_keys(
        data, 'id', 'patient_id', 'episode_id',
        'consistency_token',
        'consistency_token',
        'created_by_id', 'updated_by_id'
    )

    # Only include patient subrecords once - at the patient subrecord level
    for subrecord in subrecords.patient_subrecords():
        name = subrecord.get_api_name()
        for episode_id, episode in data['episodes'].items():
            if name in episode:
                del episode[name]

    if exclude is not None:
        for api_name in exclude.split(','):
            data = remove_keys(data, api_name)

    return data, patient
