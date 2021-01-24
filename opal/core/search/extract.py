"""
Utilities for extracting data from Opal applications
"""
import datetime
import functools
import os
import tempfile
import zipfile

from django.template import loader
from opal.core.subrecords import (
    episode_subrecords, subrecords
)
from opal.core.search.extract_rule import ModelRule, ExtractRule


def write_data_dictionary(root_dir, schema):
    file_name = "data_dictionary.html"
    full_file_name = os.path.join(root_dir, file_name)
    t = loader.get_template("extract_data_schema.html")
    # sort the dictionary by the name of the rule/subrecord
    schema = {
        k: v for k, v in sorted(schema.items(), key=lambda item: item[0])
    }
    ctx = dict(schema=schema)
    rendered = t.render(ctx)
    with open(full_file_name, "w") as f:
        f.write(rendered)
    return file_name


def generate_csv_files(root_dir, episodes, user):
    file_names = []
    data_dictionary_dict = {}
    for subrecord in subrecords():
        if getattr(subrecord, '_exclude_from_extract', False):
            continue
        if subrecord in episode_subrecords():
            rule = ModelRule(
                episodes, user, subrecord, "episode__id"
            )
        else:
            rule = ModelRule(
                episodes, user, subrecord, "patient__episode__id"
            )
        file_name = rule.write_to_file(root_dir)
        if file_name:
            file_names.append(file_name)
        data_dictionary_dict.update(rule.get_data_dictionary())

    for rule_cls in ExtractRule.list():
        rule = rule_cls(episodes, user)
        file_name = rule.write_to_file(root_dir)
        data_dictionary_dict.update(rule.get_data_dictionary())
        if not file_name:
            continue
        if isinstance(file_name, list):
            file_names.extend(file_name)
        else:
            file_names.append(file_name)
    file_names.append(
        write_data_dictionary(root_dir, data_dictionary_dict)
    )
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
        for file_name in file_names:
            full_file_name = os.path.join(root_dir, file_name)
            zip_relative_file_path = os.path.join(zipfolder, file_name)
            z.write(
                full_file_name,
                zip_relative_file_path
            )

    return target


def async_extract(user_id, criteria):
    """
    Given the user and the criteria, let's run an async extract.
    """
    from opal.core.search import tasks
    return tasks.extract.delay(user_id, criteria).id
