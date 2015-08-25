"""
Utilities for extracting data from OPAL
"""
import datetime
import csv
import os

import ffs
from ffs.contrib import archive

from opal.models import Episode
from opal.core.subrecords import episode_subrecords, patient_subrecords


def subrecord_csv(episodes, subrecord, file_name):
    """
    Given an iterable of EPISODES, the SUBRECORD we want to serialise,
    return an ExtractCSV for this subrecord for these episodes.
    """
    with open(file_name, "w") as csv_file:
        writer = csv.writer(csv_file)
        field_names = subrecord._get_fieldnames_to_extract()

        for fname in ['consistency_token', 'id']:
            if fname in field_names:
                field_names.remove(fname)

        writer.writerow(field_names)
        subrecords = subrecord.objects.filter(episode__in=episodes)
        subrecord_rows = subrecords.values_list(*field_names)
        for subrecord_row in subrecord_rows:
            writer.writerow(subrecord_row)


def episode_csv(episodes, user, file_name):
    """
    Given an iterable of EPISODES, create a CSV file containing Episode details.
    """
    with open(file_name, "w") as csv_file:
        headers = [Episode._get_fieldnames_to_serialize()]
        headers.remove('consistency_token')
        headers.append(["tagging"])
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()

        for episode in episodes:
            row = {h: str(getattr(episode, h)) for h in headers}
            row["tagging"] = ';'.join(episode.get_tag_names(user, historic=True))
            writer.writerow(row)


def patient_subrecord_csv(episodes, subrecord, file_name):
    """
    Given an iterable of EPISODES, and the patient SUBRECORD we want to
    serialise, return an ExtractCSV for this subrecord for these episodes.
    """
    with open(file_name, "w") as csv_file:
        field_names = subrecord._get_fieldnames_to_extract()
        writer = csv.writer(csv_file)

        for fname in ['consistency_token', 'patient_id', 'id']:
            if fname in field_names:
                field_names.remove(fname)

        patient_to_episode = {e.patient_id: e.id for e in episodes}
        subs = subrecord.objects.filter(patient__in=patient_to_episode.keys())

        headers = list(field_names)
        headers.insert(0, "episode_id")
        writer.writerow(headers)

        for sub in subs:
            row = [patient_to_episode[sub.patient_id]]
            row.extend(getattr(sub, f) for f in field_names)
            writer.writerow(row)


def zip_archive(episodes, description, user):
    """
    Given an iterable of EPISODES, the DESCRIPTION of this set of episodes,
    and the USER for which we are extracting, create a zip archive suitable
    for download with all of these episodes as CSVs.
    """
    csvs = []
    for subrecord in episode_subrecords():
        file_name = '{0}.csv'.format(subrecord.get_api_name())
        csvs.append(subrecord_csv(episodes, subrecord, file_name))

    csvs.append(episode_csv(episodes, user))

    target_dir = str(ffs.Path.newdir())
    target = target_dir + '/extract.zip'

    with ffs.Path.temp() as tempdir:
        with tempdir:
            zipfile = archive.ZipPath('episodes.zip')

        relative_zipfolder = '{0}.{1}'.format(user.username, datetime.date.today())
        zipfolder = os.path.join(zipfile, relative_zipfolder)
        episode_csv_file_name = os.path.join(zipfolder, "episodes.csv")
        csvs.append(episode_csv(episodes, user, episode_csv_file_name))

        for subrecord in episode_subrecords():
            file_name = '{0}.csv'.format(subrecord.get_api_name())
            full_file_name = os.path.join(zipfolder, file_name)
            csvs.append(subrecord_csv(episodes, subrecord, full_file_name))

        for subrecord in patient_subrecords():
            file_name = '{0}.csv'.format(subrecord.get_api_name())
            full_file_name = os.path.join(zipfolder, file_name)
            csvs.append(patient_subrecord_csv(episodes, subrecord, full_file_name))
            zipfolder+'filter.txt' << description.encode('UTF-8')
            ffs.mv(zipfile, target)
    return target
