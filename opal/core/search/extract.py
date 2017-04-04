"""
Utilities for extracting data from OPAL
"""
import datetime
import csv
import os
from collections import OrderedDict
import tempfile
import zipfile
import functools
import logging
from django.template import Context, loader

from opal.models import Episode
from opal.core.subrecords import (
    episode_subrecords, patient_subrecords, subrecords
)

from six import u


class CsvRender(object):
    def __init__(self, model, user):
        self.model = model
        self.user = user
        self.fields = self.get_field_names_to_render()

    def get_field_names_to_render(self):
        field_names = self.model._get_fieldnames_to_extract()
        field_names.remove("consistency_token")
        return field_names

    def get_field_title(self, field_name):
        return self.model._get_field_title(field_name)

    def get_headers(self):
        field_names = self.get_field_names_to_render()
        return [
            self.get_field_title(fn) for fn in field_names
        ]

    def get_row(self, instance):
        as_dict = instance.to_dict(user=self.user, fields=self.fields)

        result = []

        for f in self.fields:
            col_value = as_dict[f]
            if isinstance(col_value, list):
                result.append(
                    "; ".join(u(str(i).encode('UTF-8')) for i in col_value)
                )
            else:
                result.append(u(str(col_value).encode('UTF-8')))

        return result


class EpisodeCsvRender(CsvRender):
    def __init__(self, user):
        super(EpisodeCsvRender, self).__init__(Episode, user)

    def get_headers(self):
        headers = super(EpisodeCsvRender, self).get_headers()
        headers.append("Tagging")
        return headers

    def get_row(self, instance):
        row = super(EpisodeCsvRender, self).get_row(instance)
        row.append(';'.join(
            instance.get_tag_names(self.user, historic=True)
        ))
        return row

    def get_field_title(self, field_name):
        if field_name == "start" or field_name == "end":
            return field_name.title()
        else:
            return super(EpisodeCsvRender, self).get_field_title(
                field_name
            )


class PatientSubrecordCsvRender(CsvRender):
    def get_field_names_to_render(self):
        field_names = super(
            PatientSubrecordCsvRender, self
        ).get_field_names_to_render()
        field_names.remove("id")
        return field_names

    def get_headers(self):
        headers = super(PatientSubrecordCsvRender, self).get_headers()
        headers.insert(0, "Episode")
        return headers

    def get_row(self, instance, episode_id):
        row = super(PatientSubrecordCsvRender, self).get_row(instance)
        row.insert(0, str(episode_id))
        return row


class EpisodeSubrecordCsvRender(CsvRender):
    def get_field_names_to_render(self):
        field_names = super(
            EpisodeSubrecordCsvRender, self
        ).get_field_names_to_render()
        field_names.remove("id")
        return field_names

    def get_headers(self):
        headers = super(EpisodeSubrecordCsvRender, self).get_headers()
        headers.insert(0, "Patient")
        return headers

    def get_row(self, instance):
        row = super(EpisodeSubrecordCsvRender, self).get_row(instance)
        row.insert(0, str(instance.episode.patient_id))
        return row


def field_to_dict(subrecord, field_name):
    return dict(
        display_name=subrecord._get_field_title(field_name),
        description=subrecord.get_field_description(field_name),
        type_display_name=subrecord.get_human_readable_type(field_name),
    )


def get_data_dictionary():
    schema = {}
    for subrecord in subrecords():
        field_names = subrecord._get_fieldnames_to_extract()
        record_schema = [field_to_dict(subrecord, i) for i in field_names]
        schema[subrecord.get_display_name()] = record_schema
    field_names = Episode._get_fieldnames_to_extract()
    field_names.remove("start")
    field_names.remove("end")
    schema["Episode"] = [field_to_dict(Episode, i) for i in field_names]
    schema["Episode"].append(dict(
        display_name="Start",
        type_display_name="Date & Time"
    ))
    schema["Episode"].append(dict(
        display_name="End",
        type_display_name="Date & Time"
    ))
    return OrderedDict(sorted(schema.items(), key=lambda t: t[0]))


def write_data_dictionary(file_name):
    dictionary = get_data_dictionary()
    t = loader.get_template("extract_data_schema.html")
    ctx = Context(dict(schema=dictionary))
    rendered = t.render(ctx)
    with open(file_name, "w") as f:
        f.write(rendered)


def episode_subrecord_csv(episodes, user, subrecord, file_name):
    """
    Given an iterable of EPISODES, the SUBRECORD we want to serialise,
    write a csv file for the data in this subrecord for these episodes.
    """
    logging.info("writing for %s" % subrecord)
    with open(file_name, "w") as csv_file:
        writer = csv.writer(csv_file)
        extractor = EpisodeSubrecordCsvRender(subrecord, user)
        writer.writerow(extractor.get_headers())
        subrecords = subrecord.objects.filter(episode__in=episodes)
        for sub in subrecords:
            writer.writerow(extractor.get_row(sub))
    logging.info("finished writing for %s" % subrecord)


def episode_csv(episodes, user, file_name):
    """
    Given an iterable of EPISODES, create a CSV file containing
    Episode details.
    """
    logging.info("writing eposides")
    with open(file_name, "w") as csv_file:
        extractor = EpisodeCsvRender(user)
        writer = csv.writer(csv_file)
        writer.writerow(extractor.get_headers())

        for episode in episodes:
            writer.writerow(extractor.get_row(episode))

    logging.info("finished writing episodes")


def patient_subrecord_csv(episodes, user, subrecord, file_name):
    """
    Given an iterable of EPISODES, and the patient SUBRECORD we want to
    create a CSV file for the data in this subrecord for these episodes.
    """
    logging.info("writing patient subrecord %s" % subrecord)
    with open(file_name, "w") as csv_file:
        writer = csv.writer(csv_file)
        patient_to_episode = {e.patient_id: e.id for e in episodes}
        subs = subrecord.objects.filter(
            patient__in=list(patient_to_episode.keys())
        )

        extractor = PatientSubrecordCsvRender(subrecord, user)
        writer.writerow(extractor.get_headers())

        for sub in subs:
            writer.writerow(
                extractor.get_row(sub, patient_to_episode[sub.patient_id])
            )
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
            episode_subrecord_csv(episodes, user, subrecord, full_file_name)
            z.write(full_file_name, zip_relative_file_path(file_name))

        for subrecord in patient_subrecords():
            if getattr(subrecord, '_exclude_from_extract', False):
                continue
            file_name = '{0}.csv'.format(subrecord.get_api_name())
            full_file_name = make_file_path(file_name)
            patient_subrecord_csv(episodes, user, subrecord, full_file_name)
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
