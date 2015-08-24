"""
Utilities for extracting data from OPAL
"""
import datetime

import ffs
from ffs.contrib import archive

from opal.models import Episode, Tagging, EpisodeSubrecord, PatientSubrecord
from opal.core.subrecords import episode_subrecords, patient_subrecords

class ExtractCSV(object):

    def __init__(self, contents=None, filename=None):
        self.contents = contents
        self.filename = filename


def episode_csv(episodes, user):
    """
    Given an iterable of EPISODES, create a CSV file containing Episode details.
    """
    lines = []
    fieldnames = Episode._get_fieldnames_to_serialize()
    for fname in ['consistency_token']:
        if fname in fieldnames:
            fieldnames.remove(fname)
    historic = Tagging.historic_tags_for_episodes([e.id for e in episodes])

    lines.append(','.join(fieldnames) + ',tagging')
    for episode in episodes:
        items = [str(getattr(episode, f)) for f in fieldnames]
        items.append(';'.join(episode.get_tag_names(user, historic=True)))
        lines.append(','.join(items))

    contents = '\n'.join(lines)
    csv = ExtractCSV(filename='episodes.csv', contents=contents)
    return csv

def subrecord_csv(episodes, subrecord):
    """
    Given an iterable of EPISODES, the SUBRECORD we want to serialise,
    return an ExtractCSV for this subrecord for these episodes.
    """
    filename = '{0}.csv'.format(subrecord.get_api_name())
    lines = []
    fieldnames = subrecord._get_fieldnames_to_extract()
    for fname in ['consistency_token', 'id']:
        if fname in fieldnames:
            fieldnames.remove(fname)
    lines.append(u','.join(fieldnames))

    subrecords = subrecord.objects.filter(episode__in=episodes)
    for sub in subrecords:
        lines.append(u','.join([unicode(getattr(sub, f)) for f in fieldnames]))

    contents = u'\n'.join(lines)
    csv = ExtractCSV(filename=filename, contents=contents)
    return csv

def patient_subrecord_csv(episodes, subrecord):
    """
    Given an iterable of EPISODES, and the patient SUBRECORD we want to
    serialise, return an ExtractCSV for this subrecord for these episodes.
    """
    filename = '{0}.csv'.format(subrecord.get_api_name())
    lines = []
    fieldnames = subrecord._get_fieldnames_to_extract()
    for fname in ['consistency_token', 'patient_id', 'id']:
        if fname in fieldnames:
            fieldnames.remove(fname)
    lines.append(u'episode_id,' + u','.join(fieldnames))

    for episode in episodes:
        for sub in subrecord.objects.filter(patient=episode.patient):
            items = [unicode(episode.id)]
            items += [unicode(getattr(sub, f)) for f in fieldnames]
            lines.append(u','.join(items))

    contents = u'\n'.join(lines)
    csv = ExtractCSV(filename=filename, contents=contents)
    return csv


def zip_archive(episodes, description, user):
    """
    Given an iterable of EPISODES, the DESCRIPTION of this set of episodes,
    and the USER for which we are extracting, create a zip archive suitable
    for download with all of these episodes as CSVs.
    """
    csvs = []
    for sub in episode_subrecords():
        csvs.append(subrecord_csv(episodes, sub))
    for sub in patient_subrecords():
        csvs.append(patient_subrecord_csv(episodes, sub))

    csvs.append(episode_csv(episodes, user))

    target_dir = str(ffs.Path.newdir())
    target = target_dir + '/extract.zip'

    with ffs.Path.temp() as tempdir:
        zipfolder = '{0}.{1}/'.format(user.username, datetime.date.today())
        with tempdir:
            zipfile = archive.ZipPath('episodes.zip')
            for csv in csvs:
                zipfile/(zipfolder+csv.filename) << csv.contents.encode('UTF-8')
            zipfile/(zipfolder+'filter.txt') << description.encode('UTF-8')
            ffs.mv(zipfile, target)
    return target
