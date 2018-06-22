"""
Utilities for import/export of patients and episodes
"""
from django.db import transaction

from opal import models
from opal.core import match, subrecords, serialization
from opal.utils import remove_keys, remove_empty_lists


class OpalExportMatcher(match.Matcher):
    """
    Matcher for data in the Opal portable export format.
    """
    direct_match_field     = 'nhs_number'
    attribute_match_fields = [
        'date_of_birth',
        'first_name',
        'surname',
    ]

    def get_demographic_dict(self):
        return self.data


"""
Imports
"""


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
    demographics = data['demographics'][0]
    demographics['date_of_birth'] = serialization.deserialize_date(
        demographics['date_of_birth']
    )
    matcher = OpalExportMatcher(demographics)
    patient, created = matcher.match_or_create(user=user)

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


def patient_id_to_json(patient_id, user=None, excludes=None):
    """
    Given a PATIENT_ID return the JSON export of that patient and the
    patient as a tuple:

    return (DATA, PATIENT)

    If requried, pass in the active user as a kwarg.
    If required, pass in an interable of api_names as a kwarg to limit
    the subrecords you export.

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
        'created_by_id', 'updated_by_id',
        'created', 'updated'
    )

    # Only include patient subrecords once - at the patient subrecord level
    for subrecord in subrecords.patient_subrecords():
        name = subrecord.get_api_name()
        for episode_id, episode in data['episodes'].items():
            if name in episode:
                del episode[name]

    if excludes is not None:
        for api_name in excludes:
            data = remove_keys(data, api_name)

    data = remove_empty_lists(data)

    return data, patient
