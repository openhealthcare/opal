"""
Opal subrecords - helpers, iterators et cetera
"""
from opal.utils import _itersubclasses


def episode_subrecords():
    """
    Generator function for episode subrecords.
    """
    from opal.models import EpisodeSubrecord
    for model in _itersubclasses(EpisodeSubrecord):
        if model._meta.abstract or model._exclude_from_subrecords:
            continue
        yield model


def patient_subrecords():
    """
    Generator function for patient subrecords.
    """
    from opal.models import PatientSubrecord
    for model in _itersubclasses(PatientSubrecord):
        if model._meta.abstract or model._exclude_from_subrecords:
            continue
        yield model


def subrecords():
    """
    Generator function for subrecords
    """
    for m in patient_subrecords():
        yield m
    for m in episode_subrecords():
        yield m


def singletons():
    """
    Generator function for singleton subrecords
    """
    for s in subrecords():
        if s._is_singleton:
            yield s


def get_subrecord_from_api_name(api_name):
    for subrecord in subrecords():
        if subrecord.get_api_name() == api_name:
            return subrecord
    raise ValueError("unable to find a model for {}".format(api_name))


def get_subrecord_from_model_name(model_name):
    for subrecord in subrecords():
        if subrecord.__name__ == model_name:
            return subrecord
    raise ValueError("unable to find a model for {}".format(model_name))
