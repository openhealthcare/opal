"""
Utilities for extracting data from OPAL
"""
import datetime
import csv
import os
from copy import copy
from collections import namedtuple
import tempfile
import zipfile
import functools
import logging
from six import text_type, with_metaclass
from opal.models import Episode
from opal.core.subrecords import episode_subrecords, patient_subrecords


Column = namedtuple("Column", ["display_name", "value"])


class CsvRendererMetaClass(type):
    """
        a meta class that less us declare fields to
        append to the standard _get_fieldnames_to_extract
    """
    def __new__(cls, name, bases, attrs):
        _fields = [i for i, v in attrs.items() if isinstance(v, Column)]

        parents = [b for b in bases if isinstance(b, CsvRendererMetaClass)]
        for parent in parents:
            for field in parent._fields:
                if field not in _fields:
                    _fields.append(field)

        attrs["_fields"] = _fields
        return super(
            CsvRendererMetaClass, cls
        ).__new__(cls, name, bases, attrs)


class CsvRenderer(with_metaclass(CsvRendererMetaClass)):
    """
        An Abstract base class of the other csv renderers
    """
    def __init__(self, model, user):
        self.model = model
        self.user = user
        self.fields = self.get_field_names_to_render()

    def get_field_names_to_render(self):
        field_names = self.model._get_fieldnames_to_extract()
        field_names.remove("consistency_token")
        result = copy(self.__class__._fields)
        cls_fields = set(self.__class__._fields)
        for field_name in field_names:
            if field_name not in cls_fields:
                result.append(field_name)

        return result

    def get_field_title(self, field_name):
        return self.model._get_field_title(field_name)

    def get_headers(self):
        result = []
        for field in self.fields:
            if hasattr(self, field):
                result.append(getattr(self, field).display_name)
            else:
                result.append(self.get_field_title(field))
        return result

    def get_field_value(self, field_name, data):
        col_value = data[field_name]
        if isinstance(col_value, list):
            return "; ".join(text_type(i) for i in col_value)
        else:
            return text_type(col_value)

    def get_row(self, instance, *args, **kwargs):
        as_dict = instance.to_dict(user=self.user)

        result = []
        for field in self.fields:
            if hasattr(self, field):
                some_fn = getattr(self, field).value

                result.append(
                    some_fn(self, instance, *args, **kwargs)
                )
            else:
                result.append(self.get_field_value(field, as_dict))

        return result


class EpisodeCsvRenderer(CsvRenderer):
    tagging = Column(
        display_name="Tagging",
        value=lambda self, instance: text_type(";".join(
            instance.get_tag_names(self.user, historic=True)
        ))
    )

    start = Column(
        display_name="Start",
        value=lambda self, instance: instance.start
    )

    end = Column(
        display_name="End",
        value=lambda self, instance: instance.end
    )

    created = Column(
        display_name="Created",
        value=lambda self, instance: instance.created
    )

    updated = Column(
        display_name="Updated",
        value=lambda self, instance: instance.updated
    )

    created_by_id = Column(
        display_name="Created By",
        value=lambda self, instance: instance.created_by_id
    )

    updated_by_id = Column(
        display_name="Updated By",
        value=lambda self, instance: instance.updated_by_id
    )

    patient_id = Column(
        display_name="Patient",
        value=lambda self, instance: instance.patient_id
    )

    def __init__(self, user):
        super(EpisodeCsvRenderer, self).__init__(Episode, user)

    def get_headers(self):
        headers = super(EpisodeCsvRenderer, self).get_headers()
        return headers


class PatientSubrecordCsvRenderer(CsvRenderer):
    episode_id = Column(
        display_name="Episode",
        value=lambda self, instance, episode_id: text_type(episode_id)
    )

    def get_field_names_to_render(self):
        field_names = super(
            PatientSubrecordCsvRenderer, self
        ).get_field_names_to_render()
        field_names.remove("id")
        return field_names


class EpisodeSubrecordCsvRenderer(CsvRenderer):
    patient_id = Column(
        value=lambda self, instance: text_type(instance.episode.patient_id),
        display_name="Patient"
    )

    def get_field_names_to_render(self):
        field_names = super(
            EpisodeSubrecordCsvRenderer, self
        ).get_field_names_to_render()
        field_names.remove("id")
        return field_names


def episode_subrecord_csv(episodes, user, subrecord, file_name):
    """
    Given an iterable of EPISODES, the SUBRECORD we want to serialise,
    write a csv file for the data in this subrecord for these episodes.
    """
    logging.info("writing for %s" % subrecord)
    with open(file_name, "w") as csv_file:
        writer = csv.writer(csv_file)
        renderer = EpisodeSubrecordCsvRenderer(subrecord, user)
        writer.writerow(renderer.get_headers())
        subrecords = subrecord.objects.filter(episode__in=episodes)
        for sub in subrecords:
            writer.writerow(
                renderer.get_row(sub)
            )
    logging.info("finished writing for %s" % subrecord)


def episode_csv(episodes, user, file_name):
    """
    Given an iterable of EPISODES, create a CSV file containing
    Episode details.
    """
    logging.info("writing eposides")
    with open(file_name, "w") as csv_file:
        renderer = EpisodeCsvRenderer(user)
        writer = csv.writer(csv_file)
        writer.writerow(renderer.get_headers())

        for episode in episodes:
            writer.writerow(renderer.get_row(episode))

    logging.info("finished writing episodes")


def patient_subrecord_csv(episodes, user, subrecord, file_name):
    """
    Given an iterable of EPISODES, and the patient SUBRECORD we want to
    create a CSV file for the data in this subrecord for these episodes.
    """

    with open(file_name, "w") as csv_file:
        writer = csv.writer(csv_file)
        renderer = PatientSubrecordCsvRenderer(subrecord, user)
        writer.writerow(renderer.get_headers())

        patient_to_episode = {e.patient_id: e.id for e in episodes}
        subs = subrecord.objects.filter(
            patient__in=list(patient_to_episode.keys()))

        for sub in subs:
            writer.writerow(
                renderer.get_row(sub, patient_to_episode[sub.patient_id])
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
