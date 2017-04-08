"""
Utilities for extracting data from Opal applications
"""
import csv
import datetime
import functools
import logging
import os
import tempfile
import zipfile
from six import text_type, moves
from django.db.models import Count, Max
from django.utils.functional import cached_property
from collections import defaultdict
from opal.models import Episode
from opal.core.subrecords import subrecords, episode_subrecords


class CsvColumn(object):
    """ A custom column class that will render a custom value

        * name is similar to api_name on a field
          if it matches and existig field api name in the extract
          fields this will override it
        * value is that takes in whatever arguments
          are passed to get_row
        * display name is what is used in the header
    """
    def __init__(self, name, value=None, display_name=None, flat=False):
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
        CsvColumn("id", display_name="Episode"),
    )


class PatientSubrecordCsvRenderer(CsvRenderer):
    non_field_csv_columns = (
        CsvColumn(
            "episode_id",
            display_name="Episode",
            value=lambda renderer, instance, episode_id: text_type(episode_id)
        ),
    )

    def __init__(self, model, episode_queryset, user, fields=None, flat=False):
        self.patient_to_episode = defaultdict(list)

        for episode in episode_queryset:
            self.patient_to_episode[episode.patient_id].append(episode.id)

        queryset = model.objects.filter(
            patient__in=list(self.patient_to_episode.keys()))

        self.flat = flat
        super(PatientSubrecordCsvRenderer, self).__init__(
            model, queryset, user, fields
        )

    def get_field_names_to_render(self):
        field_names = super(
            PatientSubrecordCsvRenderer, self
        ).get_field_names_to_render()
        field_names.remove("id")

        if self.flat:
            for_removal = ["patient", "patient_id", "episode", "episode_id"]

            for to_remove in for_removal:
                if to_remove in field_names:
                    field_names.remove(to_remove)
        return field_names

    def get_rows(self):
        for sub in self.queryset:
            for episode_id in self.patient_to_episode[sub.patient_id]:
                yield self.get_row(sub, episode_id)

    @cached_property
    def row_length(self):
        return len(self.get_headers()) * self.repititions

    @cached_property
    def repititions(self):
        e_values = self.queryset.values("patient_id")
        annotated = e_values.annotate(Count("patient_id"))
        return annotated.aggregate(Max('patient_id__count'))[
            "patient_id__count__max"
        ]

    @cached_property
    def episode_id_to_serialised_instance_dict(self):
        episode_id_to_serialised_instance = defaultdict(list)

        for sub in self.queryset:
            for episode_id in self.patient_to_episode[sub.patient_id]:
                episode_id_to_serialised_instance[episode_id].append(
                    self.get_row(sub, episode_id)
                )

        return episode_id_to_serialised_instance

    def get_flat_row_for_episode_id(self, episode_id):
        serialised_instances = self.episode_id_to_serialised_instance_dict[
            episode_id
        ]
        row = []
        for serialised in serialised_instances:
            row.extend(serialised)
        if not len(row) == self.row_length:
            row.extend(
                "" for i in moves.xrange(self.row_length - len(row))
            )
        return row

    def get_flat_headers(self):
        result = []
        for i in moves.xrange(self.repititions):
            for header in self.get_headers():
                result.append("{0}-{1} {2}".format(
                    self.model.get_display_name(),
                    i + 1,
                    header
                ))
        return result


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
        if self.flat:
            for_removal = ["patient", "patient_id", "episode", "episode_id"]

            for to_remove in for_removal:
                if to_remove in field_names:
                    field_names.remove(to_remove)
        return field_names

    def __init__(self, model, episode_queryset, user, fields=None, flat=False):
        self.flat = flat
        queryset = model.objects.filter(episode__in=episode_queryset)

        super(EpisodeSubrecordCsvRenderer, self).__init__(
            model, queryset, user, fields
        )

    @cached_property
    def repititions(self):
        e_values = self.queryset.values("episode_id")
        annotated = e_values.annotate(Count("episode_id"))
        return annotated.aggregate(Max('episode_id__count'))[
            "episode_id__count__max"
        ]

    @cached_property
    def row_length(self):
        return len(self.get_headers()) * self.repititions

    def get_flat_row_for_episode_id(self, episode_id):
        by_episode_id = self.queryset.filter(episode_id=episode_id)
        row = []
        for instance in by_episode_id:
            row.extend(self.get_row(instance))
        if not len(row) == self.row_length:
            row.extend("" for i in moves.xrange(self.row_length - len(row)))
        return row

    def get_flat_headers(self):
        result = []
        for i in moves.xrange(self.repititions):
            for header in self.get_headers():
                result.append("{0}-{1} {2}".format(
                    self.model.get_display_name(),
                    i + 1,
                    header
                ))
        return result


def zip_flat_extract(episodes, description, user, specific_columns=None):
    # creates a zip file containing a csv where one episodie is one row
    # with all of their subrecords flattened into the one row
    # you can pass in a dictionary of specific_columns
    # this should be a dictionary of subrecord api name
    # to a list of fields from that subrecord
    # if you pass in subrecord api name and an empty array or None
    # all fields from that subrecord will be brought in
    # e.g.
    # {
    #    "demographics": ["first_name"],
    #    "allergies": []
    # }
    # will get you a give you a row with the first name
    # of demographics and all the allergies fields

    target_dir = tempfile.mkdtemp()
    target = os.path.join(target_dir, 'extract.zip')
    zipfolder = '{0}.{1}'.format(user.username, datetime.date.today())
    make_file_path = functools.partial(os.path.join, target_dir, zipfolder)
    zip_relative_file_path = functools.partial(os.path.join, zipfolder)

    if specific_columns:
        episode_api_name = "episode"
        if episode_api_name in specific_columns:
            specific_fields = specific_columns[episode_api_name]
            if specific_fields:
                for required_field in ["patient_id", "id"]:
                    if required_field not in specific_fields:
                        specific_fields.insert(0, required_field)

            episode_renderer = EpisodeCsvRenderer(
                Episode,
                episodes,
                user,
                fields=specific_fields
            )
        else:
            episode_renderer = EpisodeCsvRenderer(
                Episode,
                episodes,
                user,
                fields=["patient_id", "id"]
            )
    else:
        episode_renderer = EpisodeCsvRenderer(Episode, episodes, user)

    subrecord_renderers = []

    for subrecord in subrecords():
        specific_fields = None

        if specific_columns:
            if subrecord.get_api_name() not in specific_columns:
                continue
            else:
                specific_fields = specific_columns[subrecord.get_api_name()]

        if getattr(subrecord, '_exclude_from_extract', False):
            continue

        if subrecord in episode_subrecords():
            renderer = EpisodeSubrecordCsvRenderer(
                subrecord, episodes, user, flat=True, fields=specific_fields
            )
        else:
            renderer = PatientSubrecordCsvRenderer(
                subrecord, episodes, user, flat=True, fields=specific_fields
            )
        if renderer.count():
            subrecord_renderers.append(renderer)

    zipfolder = '{0}.{1}'.format(user.username, datetime.date.today())
    os.mkdir(os.path.join(target_dir, zipfolder))
    make_file_path = functools.partial(os.path.join, target_dir, zipfolder)
    file_name = "extract.csv"
    full_file_name = make_file_path(file_name)

    with open(full_file_name, "w") as csv_file:
        writer = csv.writer(csv_file)
        headers = episode_renderer.get_headers()
        for renderer in subrecord_renderers:
            headers.extend(renderer.get_flat_headers())
        writer.writerow(headers)

        for episode in episodes:
            row = episode_renderer.get_row(episode)

            for renderer in subrecord_renderers:
                row.extend(renderer.get_flat_row_for_episode_id(episode.id))
            writer.writerow(row)

    with zipfile.ZipFile(target, mode='w') as z:
        z.write(full_file_name, zip_relative_file_path(file_name))

    return target


def zip_nested_extract(episodes, description, user):
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
            if renderer.count():
                renderer.write_to_file(full_file_name)
                z.write(full_file_name, zip_relative_file_path(file_name))

    return target


def async_extract(user, criteria):
    """
    Given the user and the criteria, let's run an async extract.
    """
    from opal.core.search import tasks
    return tasks.extract.delay(user, criteria).id
