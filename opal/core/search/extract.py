"""
Utilities for extracting data from Opal applications
"""
import csv
import datetime
import functools

import os
import tempfile
import zipfile

from opal.core.search.extract_serialisers import ExtractCsvSerialiser

from django.conf import settings
from django.template import Context, loader


def chunk_list(some_list, amount):
    for i in range(0, len(some_list), amount):
        yield some_list[i:i + amount]


def write_data_dictionary(file_name):
    t = loader.get_template("data_dictionary_download.html")
    schema = ExtractCsvSerialiser.get_data_dictionary_schema()
    ctx = Context(dict(
        settings=settings,
        schema=schema,
        chunked_columns=chunk_list(schema, 5)
    ))
    rendered = t.render(ctx)
    with open(file_name, "w") as f:
        f.write(rendered)


def generate_nested_csv_extract(root_dir, episodes, user, field_dict):
    """ Generate a a single csv file and the data dictionary

        The field_dict should be {api_name: [field_names]}

        The csv file will only contain the files mentioned in the field_dict
    """
    file_names = []
    data_dict_file_name = "data_dictionary.html"
    full_file_name = os.path.join(root_dir, data_dict_file_name)
    write_data_dictionary(full_file_name)
    file_names.append((full_file_name, data_dict_file_name,))
    csv_file_name = "extract.csv"
    full_file_name = os.path.join(root_dir, csv_file_name)
    file_names.append((full_file_name, csv_file_name,))
    renderers = []
    slugs_to_serialisers = ExtractCsvSerialiser.api_name_to_serialiser_cls()

    for model_api_name, model_fields in field_dict.items():
        serialiser_cls = slugs_to_serialisers.get(model_api_name, None)

        if not serialiser_cls:
            # if for whatever reason someone tries to extract a model api name
            # we don't allow, just skip it
            continue
        model = ExtractCsvSerialiser.get_model_for_api_name(model_api_name)

        renderers.append(serialiser_cls(
            model, episodes, user, fields=field_dict[model_api_name]
        ))

    with open(full_file_name, 'w') as csv_file:
        writer = csv.writer(csv_file)
        headers = []
        for renderer in renderers:
            headers.extend(renderer.get_flat_headers())
        writer.writerow(headers)

        for episode in episodes:
            row = []
            for renderer in renderers:
                row.extend(renderer.get_nested_row(episode))
            writer.writerow(row)
    return file_names


def generate_multi_csv_extract(root_dir, episodes, user):
    """ Generate the files and return a tuple of absolute_file_name, file_name
    """
    file_names = []

    file_name = "data_dictionary.html"
    full_file_name = os.path.join(root_dir, file_name)
    write_data_dictionary(full_file_name)
    file_names.append((full_file_name, file_name,))

    full_file_name = os.path.join(root_dir, file_name)
    slugs_to_serialisers = ExtractCsvSerialiser.api_name_to_serialiser_cls()

    for slug, serialiser_cls in slugs_to_serialisers.items():
        file_name = "{}.csv".format(slug)
        full_file_name = os.path.join(root_dir, file_name)
        model = ExtractCsvSerialiser.get_model_for_api_name(slug)
        renderer = serialiser_cls(model, episodes, user)
        if renderer.exists():
            renderer.write_to_file(full_file_name)
            file_names.append((full_file_name, file_name,))

    return file_names


def get_description_with_fields(episodes, user, description, fields):
    field_description = []
    slugs_to_serialisers = ExtractCsvSerialiser.api_name_to_serialiser_cls()

    for serialiser_api_name, subrecord_fields in fields.items():
        serialiser_cls = slugs_to_serialisers.get(serialiser_api_name, None)
        if not serialiser_cls:
            continue
        model = ExtractCsvSerialiser.get_model_for_api_name(
            serialiser_api_name
        )

        serialiser = serialiser_cls(model, episodes, user, fields=fields)

        field_names = ", ".join(
            serialiser.get_field_title(i) for i in subrecord_fields
        )
        field_description.append(
            "{} - {}".format(
                serialiser.get_display_name(),
                field_names
            )
        )
    if field_description:
        return "{description} \nExtracting:\n{fields}".format(
            description=description,
            fields="\n".join(field_description)
        )

    # ie where someone is trying to extract a subrecord
    # that is not extractable
    return description


def write_description(episodes, user, description, root_dir, fields=None):
    query_file_name = "query.txt"
    full_query_file_name = os.path.join(root_dir, query_file_name)
    if fields:
        description = get_description_with_fields(
            episodes, user, description, fields
        )

    with open(full_query_file_name, "w") as f:
        f.write(description)

    return full_query_file_name, query_file_name


def zip_archive(episodes, description, user, fields=None):
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
        full_query_file_name, query_file_name = write_description(
            episodes, user, description, root_dir, fields=fields
        )
        z.write(full_query_file_name, zip_relative_file_path(query_file_name))

        if fields:
            file_names = generate_nested_csv_extract(
                root_dir, episodes, user, fields
            )
        else:
            file_names = generate_multi_csv_extract(root_dir, episodes, user)

        for full_file_name, file_name in file_names:
            z.write(
                full_file_name,
                zip_relative_file_path(file_name)
            )

    return target


def async_extract(user, extract_query):
    """
    Given the user and the criteria, let's run an async extract.
    """
    from opal.core.search import tasks
    return tasks.extract.delay(user, extract_query).id
