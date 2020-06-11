"""
Utilities for extracting data from Opal applications
"""
from collections import OrderedDict
import csv
import datetime
import functools
import json
import logging
import os
import tempfile
import zipfile

from django.template import loader
from django.core.serializers.json import DjangoJSONEncoder
from six import text_type

from collections import defaultdict
from opal.models import Episode
from opal.core.subrecords import (
    episode_subrecords, subrecords
)


class CsvColumn(object):
    """ A custom column class that will render a custom value

        * name is similar to api_name on a field
          if it matches and existig field api name in the extract
          fields this will override it
        * value is that takes in whatever arguments
          are passed to get_row
        * display name is what is used in the header
    """
    def __init__(self, name, value=None, display_name=None):
        self.name = name
        self.value = value

        if value:
            self.value = value
        else:
            self.value = lambda renderer, obj: getattr(obj, self.name)

        if display_name:
            self.display_name = display_name
        else:
            self.display_name = self.name.title()


class CsvRenderer(object):
    """
        An Abstract base class of the other csv renderers
    """

    # overrides of model fields for the csv columns
    non_field_csv_columns = []

    def __init__(self, model, queryset, user, fields=None):
        self.queryset = queryset
        self.model = model
        self.user = user
        if fields:
            self.fields = fields
        else:
            self.fields = self.get_field_names_to_render()

    def get_non_field_csv_column_names(self):
        return [csv_column.name for csv_column in self.non_field_csv_columns]

    def get_non_field_csv_columns(self, field_name):
        return next(
            i for i in self.non_field_csv_columns if i.name == field_name
        )

    def get_field_names_to_render(self):
        field_names = self.model._get_fieldnames_to_extract()
        field_names.remove("consistency_token")
        result = self.get_non_field_csv_column_names()
        non_field_csv_columns_set = set(result)
        for field_name in field_names:
            if field_name not in non_field_csv_columns_set:
                result.append(field_name)

        return result

    def get_field_title(self, field_name):
        return self.model._get_field_title(field_name)

    def get_headers(self):
        result = []
        for field in self.fields:
            if field in self.get_non_field_csv_column_names():
                result.append(
                    self.get_non_field_csv_columns(field).display_name
                )
            else:
                result.append(self.get_field_title(field))
        return result

    def serialize_dict(self, some_dict):
        return json.dumps(some_dict, cls=DjangoJSONEncoder)

    def serialize_list(self, some_list):
        """
        Complex datatypes (ie anything that involves a dict)
        should be json serialized, otherwise, return a
        semicolon seperated list
        """
        if len(some_list) and isinstance(some_list[0], dict):
            return json.dumps(some_list, cls=DjangoJSONEncoder)
        else:
            return "; ".join(text_type(i) for i in some_list)

    def serialize_value(self, some_value):
        if isinstance(some_value, list):
            return self.serialize_list(some_value)
        if isinstance(some_value, dict):
            return self.serialize_dict(some_value)
        return text_type(some_value)

    def get_field_value(self, field_name, data):
        return self.serialize_value(data[field_name])

    def get_row(self, instance, *args, **kwargs):
        as_dict = instance.to_dict(user=self.user)

        result = []

        for field in self.fields:
            if field in self.get_non_field_csv_column_names():
                some_fn = self.get_non_field_csv_columns(field).value
                result.append(
                    some_fn(self, instance, *args, **kwargs)
                )
            else:
                result.append(self.get_field_value(field, as_dict))
        return result

    def get_rows(self):
        for instance in self.queryset:
            yield self.get_row(instance)

    def count(self):
        return self.queryset.count()

    def write_to_file(self, file_name):
        logging.info("writing for {}".format(self.model))

        with open(file_name, "w") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(self.get_headers())
            for row in self.get_rows():
                writer.writerow(row)

        logging.info("finished writing for {}".format(self.model))


class EpisodeCsvRenderer(CsvRenderer):
    non_field_csv_columns = (
        CsvColumn(
            "tagging",
            value=lambda renderer, instance: text_type(";".join(
                instance.get_tag_names(renderer.user, historic=True)
            ))
        ),
        CsvColumn("start"),
        CsvColumn("end"),
        CsvColumn("created"),
        CsvColumn("updated"),
        CsvColumn("created_by_id", display_name="Created By"),
        CsvColumn("updated_by_id", display_name="Updated By"),
        CsvColumn("patient_id", display_name="Patient"),
    )


class PatientSubrecordCsvRenderer(CsvRenderer):
    non_field_csv_columns = (
        CsvColumn(
            "episode_id",
            display_name="Episode",
            value=lambda renderer, instance, episode_id: text_type(episode_id)
        ),
    )

    def __init__(self, model, episode_queryset, user, fields=None):
        self.patient_to_episode = defaultdict(list)

        for episode in episode_queryset:
            self.patient_to_episode[episode.patient_id].append(episode.id)

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
            for episode_id in self.patient_to_episode[sub.patient_id]:
                yield self.get_row(sub, episode_id)


def field_to_dict(subrecord, field_name):
    return dict(
        display_name=subrecord._get_field_title(field_name),
        description=subrecord.get_field_description(field_name),
        type_display_name=subrecord.get_human_readable_type(field_name),
    )


def get_data_dictionary():
    schema = {}
    for subrecord in subrecords():
        if getattr(subrecord, '_exclude_from_extract', False):
            continue

        field_names = subrecord._get_fieldnames_to_extract()
        record_schema = [field_to_dict(subrecord, i) for i in field_names]
        schema[subrecord.get_display_name()] = record_schema
    field_names = Episode._get_fieldnames_to_extract()
    schema["Episode"] = [field_to_dict(Episode, i) for i in field_names]
    return OrderedDict(sorted(schema.items(), key=lambda t: t[0]))


def write_data_dictionary(file_name):
    dictionary = get_data_dictionary()
    t = loader.get_template("extract_data_schema.html")
    ctx = dict(schema=dictionary)
    rendered = t.render(ctx)
    with open(file_name, "w") as f:
        f.write(rendered)


class EpisodeSubrecordCsvRenderer(CsvRenderer):
    non_field_csv_columns = (
        CsvColumn(
            "patient_id",
            display_name="Patient",
            value=lambda self, instance: text_type(instance.episode.patient_id)
        ),
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


def generate_csv_files(root_dir, episodes, user):
    """ Generate the files and return a tuple of absolute_file_name, file_name
    """
    file_names = []

    file_name = "data_dictionary.html"
    full_file_name = os.path.join(root_dir, file_name)
    write_data_dictionary(full_file_name)
    file_names.append((full_file_name, file_name,))

    file_name = "episodes.csv"
    full_file_name = os.path.join(root_dir, file_name)
    renderer = EpisodeCsvRenderer(Episode, episodes, user)
    renderer.write_to_file(full_file_name)
    file_names.append((full_file_name, file_name,))

    for subrecord in subrecords():
        if getattr(subrecord, '_exclude_from_extract', False):
            continue
        file_name = '{0}.csv'.format(subrecord.get_api_name())
        full_file_name = os.path.join(root_dir, file_name)
        if subrecord in episode_subrecords():
            renderer = EpisodeSubrecordCsvRenderer(
                subrecord, episodes, user
            )
        else:
            renderer = PatientSubrecordCsvRenderer(
                subrecord, episodes, user
            )
        if renderer.count():
            renderer.write_to_file(full_file_name)
            file_names.append((full_file_name, file_name,))

    return file_names


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
        root_dir = os.path.join(target_dir, zipfolder)
        os.mkdir(root_dir)
        zip_relative_file_path = functools.partial(os.path.join, zipfolder)
        file_names = generate_csv_files(root_dir, episodes, user)
        for full_file_name, file_name in file_names:
            z.write(
                full_file_name,
                zip_relative_file_path(file_name)
            )

    return target


def async_extract(user, criteria):
    """
    Given the user and the criteria, let's run an async extract.
    """
    from opal.core.search import tasks
    return tasks.extract.delay(user, criteria).id
