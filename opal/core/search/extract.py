"""
Utilities for extracting data from OPAL
"""
import datetime
import csv
import os
import tempfile
import zipfile
import functools
import logging

from opal.models import Episode
from opal.core.subrecords import episode_subrecords, patient_subrecords

from six import u


def subrecord_csv(episodes, subrecord, file_name):
    """
    Given an iterable of EPISODES, the SUBRECORD we want to serialise,
    write a csv file for the data in this subrecord for these episodes.
    """
    logging.info("writing for %s" % subrecord)
    with open(file_name, "w") as csv_file:
        writer = csv.writer(csv_file)
        field_names = subrecord._get_fieldnames_to_extract()

        for fname in ['consistency_token', 'id']:
            if fname in field_names:
                field_names.remove(fname)

        writer.writerow(field_names)
        subrecords = subrecord.objects.filter(episode__in=episodes)
        for sub in subrecords:
            writer.writerow([
                u(str(getattr(sub, f))) for f in field_names
            ])
    logging.info("finished writing for %s" % subrecord)


def episode_csv(episodes, user, file_name):
    """
    Given an iterable of EPISODES, create a CSV file containing
    Episode details.
    """
    logging.info("writing eposides")
    with open(file_name, "w") as csv_file:
        fieldnames = Episode._get_fieldnames_to_serialize()
        fieldnames.remove('consistency_token')
        headers = list(fieldnames)
        headers.append("tagging")
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()

        for episode in episodes:
            row = {
                h: str(getattr(episode, h)).encode('UTF-8') for h in fieldnames
            }
            row["tagging"] = ';'.join(
                episode.get_tag_names(user, historic=True)
            )
            writer.writerow(row)
    logging.info("finished writing episodes")


def patient_subrecord_csv(episodes, subrecord, file_name):
    """
    Given an iterable of EPISODES, and the patient SUBRECORD we want to
    create a CSV file for the data in this subrecord for these episodes.
    """
    logging.info("writing patient subrecord %s" % subrecord)
    with open(file_name, "w") as csv_file:
        field_names = subrecord._get_fieldnames_to_extract()
        writer = csv.writer(csv_file)

        for fname in ['consistency_token', 'patient_id', 'id']:
            if fname in field_names:
                field_names.remove(fname)

        patient_to_episode = {e.patient_id: e.id for e in episodes}
        subs = subrecord.objects.filter(
            patient__in=list(patient_to_episode.keys()))

        headers = list(field_names)
        headers.insert(0, "episode_id")
        writer.writerow(headers)

        for sub in subs:
            row = [patient_to_episode[sub.patient_id]]
            row.extend(u(str(getattr(sub, f))) for f in field_names)
            writer.writerow(row)
    logging.info("finished patient subrecord %s" % subrecord)


def zip_archive(episodes, description, user):
    """
    Given an iterable of EPISODES, the DESCRIPTION of this set of episodes,
    and the USER for which we are extracting, create a zip archive suitable
    for download with all of these episodes as CSVs.
    """
    target_dir = tempfile.mkdtemp()
    target = os.path.join(target_dir, 'extract.zip')

    with zipfile.ZipFile(target, mode='w') as z:
        zipfolder = '{0}.{1}'.format(user.username, datetime.date.today())
        os.mkdir(os.path.join(target_dir, zipfolder))
        make_file_path = functools.partial(os.path.join, target_dir, zipfolder)
        zip_relative_file_path = functools.partial(os.path.join, zipfolder)

        file_name = "episodes.csv"
        full_file_name = make_file_path(file_name)
        episode_csv(episodes, user, full_file_name)
        z.write(full_file_name, zip_relative_file_path(file_name))

        for subrecord in episode_subrecords():
            if getattr(subrecord, '_exclude_from_extract', False):
                continue
            file_name = '{0}.csv'.format(subrecord.get_api_name())
            full_file_name = make_file_path(file_name)
            subrecord_csv(episodes, subrecord, full_file_name)
            z.write(full_file_name, zip_relative_file_path(file_name))

        for subrecord in patient_subrecords():
            if getattr(subrecord, '_exclude_from_extract', False):
                continue
            file_name = '{0}.csv'.format(subrecord.get_api_name())
            full_file_name = make_file_path(file_name)
            patient_subrecord_csv(episodes, subrecord, full_file_name)
            z.write(full_file_name, zip_relative_file_path(file_name))

        file_name = 'filter.txt'
        full_file_name = make_file_path(file_name)
        with open(full_file_name, 'w') as description_file:
            description_file.write(description)
        z.write(full_file_name, zip_relative_file_path(file_name))

    return target


def async_extract(user, criteria):
    """
    Given the user and the criteria, let's run an async extract.
    """
    from opal.core.search import tasks
    return tasks.extract.delay(user, criteria).id
