"""
Tagging Opal episodes
"""
from __future__ import unicode_literals

from opal.core import patient_lists


def parent(tag):
    """
    Returns the parent tag, or None if the current
    tag has no parent.
    """
    for tlist in patient_lists.TaggedPatientList.list():
        if getattr(tlist, 'subtag', None) == tag:
            return tlist.tag
    return
