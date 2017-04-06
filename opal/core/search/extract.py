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
from opal.core.subrecords import subrecords, episode_subrecords


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
    def __init__(self, model, queryset, user, fields=None):
        self.queryset = queryset
        self.model = model
        self.user = user
        if fields:
            self.fields = fields
        else:
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

    def get_rows(self):
        for instance in self.queryset:
            yield self.get_row(instance)

    def write_to_file(self, file_name):
        logging.info("writing for {}".format(self.model))
        with open(file_name, "w") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(self.get_headers())
            for row in self.get_rows():
                writer.writerow(row)

        logging.info("finished writing for {}".format(self.model))


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


class PatientSubrecordCsvRenderer(CsvRenderer):
    episode_id = Column(
        display_name="Episode",
        value=lambda self, instance, episode_id: text_type(episode_id)
    )

    def __init__(self, model, episode_queryset, user, fields=None):
        self.patient_to_episode = {
            e.patient_id: e.id for e in episode_queryset
        }
        queryset = model.objects.filter(
            patient__in=list(self.patient_to_episode.keys()))

        super(PatientSubrecordCsvRenderer, self).__init__(
            model, queryset, user, fields
        )

    def get_field_names_to_render(self):
        field_names = super(
            PatientSubrecordCsvRenderer, self
        ).get_field_names_to_render()
        field_names.remove("id")
        return field_names

    def get_rows(self):
        for sub in self.queryset:
            yield self.get_row(sub, self.patient_to_episode[sub.patient_id])


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

    def __init__(self, model, episode_queryset, user, fields=None):
        queryset = model.objects.filter(episode__in=episode_queryset)

        super(EpisodeSubrecordCsvRenderer, self).__init__(
            model, queryset, user, fields
        )


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
        renderer = EpisodeCsvRenderer(Episode, episodes, user)
        renderer.write_to_file(full_file_name)
        z.write(full_file_name, zip_relative_file_path(file_name))

        for subrecord in subrecords():
            if getattr(subrecord, '_exclude_from_extract', False):
                continue
            file_name = '{0}.csv'.format(subrecord.get_api_name())
            full_file_name = make_file_path(file_name)
            if subrecord in episode_subrecords():
                renderer = EpisodeSubrecordCsvRenderer(
                    subrecord, episodes, user
                )
            else:
                renderer = PatientSubrecordCsvRenderer(
                    subrecord, episodes, user
                )

            renderer.write_to_file(full_file_name)
            z.write(full_file_name, zip_relative_file_path(file_name))

    return target


def async_extract(user, criteria):
    """
    Given the user and the criteria, let's run an async extract.
    """
    from opal.core.search import tasks
    return tasks.extract.delay(user, criteria).id
