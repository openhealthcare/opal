import itertools
import logging
import csv

from collections import defaultdict
from six import text_type
from django.utils.functional import cached_property
from django.db.models import Count, Max
from django.utils.encoding import force_bytes

from opal.core import discoverable
from opal.core.search import schemas
from opal.models import Episode
from opal.core import subrecords


def _encode_to_utf8(some_var):
    if not isinstance(some_var, text_type):
        return some_var
    else:
        return force_bytes(some_var)


class CsvColumn(object):
    """ A custom column class that will render a custom value

        * name is similar to api_name on a field
          if it matches and existig field api name in the extract
          fields this will override it
        * value is that takes in whatever arguments
          are passed to get_row
        * display name is what is used in the header
    """
    def __init__(self, name, value=None, display_name=None, description=None):
        self.name = name
        self.value = value
        self.description = description

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

    def exists(self):
        return self.queryset.exists()

    def get_field_names_to_render(self):
        field_names = self.model._get_fieldnames_to_extract()
        # its not in episode but its in all subrecords
        if "consistency_token" in field_names:
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
        return [_encode_to_utf8(i) for i in result]

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
                writer.writerow([i for i in row])

        logging.info("finished writing for {}".format(self.model))

    @cached_property
    def flat_row_length(self):
        return len(self.get_flat_headers())

    def get_flat_headers(self):
        single_headers = self.get_headers()

        if self.flat_repetitions == 1:
            return [
                "{0} {1}".format(
                    self.model.get_display_name(),
                    i
                ) for i in single_headers
            ]

        result = []

        for rep in range(self.flat_repetitions):
            result.extend(
                (
                    "{0} {1} {2}".format(
                        self.model.get_display_name(),
                        rep + 1,
                        i
                    ) for i in single_headers
                )
            )
        return result

    @classmethod
    def get_schema(cls, some_model):
        return schemas.extract_download_schema_for_model(some_model)


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

    def get_display_name(self):
        return self.model.get_display_name()

    def get_rows(self):
        for sub in self.queryset:
            for episode_id in self.patient_to_episode[sub.patient_id]:
                yield self.get_row(sub, episode_id)

    @cached_property
    def flat_repetitions(self):
        if not self.queryset.exists():
            return 0

        if self.model._is_singleton:
            return 1

        annotated = self.queryset.values('patient_id').annotate(
            Count('patient_id')
        )
        return annotated.aggregate(Max('patient_id__count'))[
            "patient_id__count__max"
        ]

    def get_nested_row(self, episode):
        nested_subrecords = self.queryset.filter(
            patient__episode=episode
        )
        result = []
        for nested_subrecord in nested_subrecords:
            result.extend(self.get_row(nested_subrecord, episode.id))

        while len(result) < self.flat_row_length:
            result.append('')
        return result


class EpisodeSubrecordCsvRenderer(CsvRenderer):
    non_field_csv_columns = (
        CsvColumn(
            "patient_id",
            display_name="Patient",
            value=lambda self, instance: text_type(instance.episode.patient_id)
        ),
    )

    def __init__(self, model, episode_queryset, user, fields=None):
        queryset = model.objects.filter(episode__in=episode_queryset)

        super(EpisodeSubrecordCsvRenderer, self).__init__(
            model, queryset, user, fields
        )

    def get_field_names_to_render(self):
        field_names = super(
            EpisodeSubrecordCsvRenderer, self
        ).get_field_names_to_render()
        field_names.remove("id")
        return field_names

    def get_display_name(self):
        return self.model.get_display_name()

    @cached_property
    def flat_repetitions(self):
        if not self.queryset:
            return 0

        if self.model._is_singleton:
            return 1

        annotated = self.queryset.values('episode_id').annotate(
            Count('episode_id')
        )
        return annotated.aggregate(Max('episode_id__count'))[
            "episode_id__count__max"
        ]

    def get_nested_row(self, episode):
        nested_subrecords = self.queryset.filter(episode=episode)
        result = []
        for nested_subrecord in nested_subrecords:
            result.extend(self.get_row(nested_subrecord))

        while len(result) < self.flat_row_length:
            result.append('')
        return result


class ExtractCsvSerialiser(CsvRenderer, discoverable.DiscoverableFeature):
    module_name = 'extract_serialisers'

    @classmethod
    def api_name_to_serialiser_cls(cls):
        slugs_to_serialiser = {i.get_slug(): i for i in cls.list()}

        patient_subrecords_api_names = {
            i.get_api_name() for i in subrecords.patient_subrecords()
        }
        for subrecord in subrecords.subrecords():
            api_name = subrecord.get_api_name()
            if api_name in slugs_to_serialiser:
                continue

            if subrecord._advanced_searchable:
                if api_name in patient_subrecords_api_names:
                    slugs_to_serialiser[api_name] = PatientSubrecordCsvRenderer
                else:
                    slugs_to_serialiser[api_name] = EpisodeSubrecordCsvRenderer
        return slugs_to_serialiser

    @classmethod
    def get_model_for_api_name(cls, api_name):
        if api_name == "episode":
            return Episode
        return subrecords.get_subrecord_from_api_name(api_name)

    @classmethod
    def get_data_dictionary_schema(cls):
        result = []
        api_name_to_serialiser_cls = cls.api_name_to_serialiser_cls()
        subrecords_and_episode = itertools.chain(
            subrecords.subrecords(), [Episode]
        )
        for some_model in subrecords_and_episode:
            # there will be no schema if its advanced searchable false
            # and hasn't been overridden
            serialiser_cls = api_name_to_serialiser_cls.get(
                some_model.get_api_name(), None
            )
            if serialiser_cls:
                result.append(
                    serialiser_cls.get_schema(some_model)
                )
        return sorted(result, key=lambda x: x["display_name"])


class EpisodeCsvRenderer(ExtractCsvSerialiser):
    display_name = "Episode"
    slug = "episode"
    non_field_csv_columns = (
        CsvColumn(
            "team",
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

    def exists(self):
        # always have an episodes file
        return True

    def get_display_name(self):
        return self.model.get_display_name()

    def get_flat_headers(self):
        single_headers = super(
            EpisodeCsvRenderer, self
        ).get_headers()

        return ["Episode {}".format(i) for i in single_headers]

    def get_nested_row(self, episode):
        return super(EpisodeCsvRenderer, self).get_row(
            episode
        )

    @classmethod
    def get_schema(cls, episode_cls):
        schema = super(EpisodeCsvRenderer, cls).get_schema(episode_cls)
        schema["fields"].append(dict(
            name="team",
            title="Team",
            type="string",
            type_display_name="Text Field"
        ))
        schema["fields"] = sorted(
            schema["fields"], key=lambda x: x["title"]
        )
        return schema
