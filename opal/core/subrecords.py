"""
OPAL subrecords - helpers, iterators et cetera
"""
from opal.utils import _itersubclasses

def episode_subrecords():
    """
    Generator function for episode subrecords.
    """
    from opal.models import EpisodeSubrecord
    for model in _itersubclasses(EpisodeSubrecord):
        if model._meta.abstract:
            continue
        yield model

def patient_subrecords():
    """
    Generator function for patient subrecords.
    """
    from opal.models import PatientSubrecord
    for model in _itersubclasses(PatientSubrecord):
        if model._meta.abstract:
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
