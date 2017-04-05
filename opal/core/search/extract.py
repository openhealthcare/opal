"""
Utilities for extracting data from OPAL
"""
import datetime
import csv
import os
from collections import OrderedDict, namedtuple
import tempfile
import zipfile
import functools
import logging
from django.template import Context, loader

from opal.models import Episode
from opal.core.subrecords import (
    episode_subrecords, patient_subrecords, subrecords
)

from six import with_metaclass
from django.utils.translation import ugettext as _

Column = namedtuple("Column", ["display_name", "value"])


class CsvRendererMetaClass(type):
    def __new__(cls, name, bases, attrs):
        _fields = []
        for field_name, val in attrs.items():
            if isinstance(val, Column):
                _fields.append(field_name)

        parents = [b for b in bases if isinstance(b, CsvRendererMetaClass)]
        for parent in parents:
            for field in parent._fields:
                if field not in _fields:
                    _fields.append(field_name)

        attrs["_fields"] = _fields
        return super(
            CsvRendererMetaClass, cls
        ).__new__(cls, name, bases, attrs)


class CsvRenderer(with_metaclass(CsvRendererMetaClass)):
    """
        An Abstract base class of the other csv renderers
    """
    def __init__(self, model, user, fields=None):
        self.model = model
        self.user = user
        if fields:
            self.fields = fields
        else:
            self.fields = self.get_field_names_to_render()

    def get_field_names_to_render(self):
        field_names = self.model._get_fieldnames_to_extract()
        field_names.remove("consistency_token")
        return self.__class__._fields + field_names

    def get_field_title(self, field_name):
        return self.model._get_field_title(field_name)

    def get_field_value(self, field_name, data):
        col_value = data[field_name]
        if isinstance(col_value, list):
            return "; ".join(_(str(i).encode('UTF-8')) for i in col_value)
        else:
            return _(str(col_value))

    def get_headers(self):
        result = []
        for field in self.fields:
            if hasattr(self, field):
                result.append(_(getattr(self, field).display_name))
            else:
                result.append(_(self.get_field_title(field)))
        return result

    def get_row(self, instance, *args, **kwargs):
        fields = [i for i in self.fields if not hasattr(self, i)]
        as_dict = instance.to_dict(user=self.user, fields=fields)

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
        value=lambda self, instance: _("; ".join(
            instance.get_tag_names(self.user)
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

    def __init__(self, user, fields=None):
        super(EpisodeCsvRenderer, self).__init__(Episode, user, fields=fields)

    def get_field_names_to_render(self):
        field_names = super(
            EpisodeCsvRenderer, self
        ).get_field_names_to_render()
        field_names.append("tagging")
        return field_names


class PatientSubrecordCsvRenderer(CsvRenderer):
    episode = Column(
        display_name="Episode",
        value=lambda self, instance, episode_id: _(str(episode_id))
    )

    def get_field_names_to_render(self):
        field_names = super(
            PatientSubrecordCsvRenderer, self
        ).get_field_names_to_render()
        field_names.remove("id")
        return field_names


class EpisodeSubrecordCsvRenderer(CsvRenderer):
    patient = Column(
        display_name="Patient",
        value=lambda self, instance: _(str(instance.episode.patient_id))
    )

    def get_field_names_to_render(self):
        field_names = super(
            EpisodeSubrecordCsvRenderer, self
        ).get_field_names_to_render()
        field_names.remove("id")
        return field_names


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
        extractor = EpisodeSubrecordCsvRenderer(subrecord, user)
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
        extractor = EpisodeCsvRenderer(user)
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

        extractor = PatientSubrecordCsvRenderer(subrecord, user)
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
