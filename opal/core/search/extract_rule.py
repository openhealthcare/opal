import csv
import os
from collections import defaultdict
from opal.core.discoverable import DiscoverableFeature
from opal.models import Episode
import json
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from opal.utils import AbstractBase


def default_base_fields(user):
    return {
        "patient_id": "Patient",
        "id": "Episode",
    }


BASE_FIELDS = getattr(settings, "BASE_FIELDS", default_base_fields)


class ExtractRule(DiscoverableFeature):
    module_name = "extract_rule"

    def __init__(self, episode_list, user):
        self.episode_list = episode_list
        self.user = user

    def write_to_file(self, directory):
        """
        Write to a file and return the name of the file written to.
        If multiple files have been written to, return a list.
        """
        pass

    def get_data_dictionary(self):
        """
        return {
            {{ display_name }}: [{
                display_name: {{ field display name }},
                description: {{ field description }},
                type_display_name: {{ field type }},
            }]
        }
        """
        return {}


class ModelRule(ExtractRule, AbstractBase):
    """
    Extract an queryset into a file.

    Takes in an episode queryset, user, model and a path that links the
    model to an episode id.

    e.g. for a patient subrecord Allergy

    it would take (episode_qs, user, Allergy, 'patient__episode__id').

    The output is a csv with the field names of a combination of
    the base fields that should appear in every csv, by default episode id
    and the fields from model._get_fieldnames_to_extract.

    The method is a combination of three things...
    1. model_id_to_episode_ids_dict a dict of the instance id to episode ids
    2. base_field_dict a dict of episode_ids to the values that should appear on every row
       (by default episode id)
    3. the output of get_instance_dict(instance) that returns serializes an instance to a dict
    """
    additional_fields = []

    def __init__(self, episode_list, user, model, path_to_episode_id):
        self.episode_list = episode_list
        self.user = user
        self.model = model
        self.path_to_episode_id = path_to_episode_id
        self.model_field_name_to_display_name = self.get_fields_name_to_display_name()

        # a dictionary of model id to epis
        self.model_id_to_episode_ids_dict = self.get_model_id_to_episode_ids()

        # the model queryset
        self.queryset = self.model.objects.filter(
            id__in=self.model_id_to_episode_ids_dict.keys()
        )

        # the additional fields that will be attatched to every row
        # e.g. patient__demographics__surname
        self.base_fields = BASE_FIELDS(user)

        # a dict of episode id to base fields
        self.base_field_dict = self.get_base_field_dict()
        self.validate_additional_fields()

    def validate_additional_fields(self):
        for field in self.additional_fields:
            extract_method = "extract_{}".format(field)
            get_field_description_method = "get_{}_description".format(field)
            if not hasattr(self.model, field) and not hasattr(self, extract_method):
                err_message = " ".join((
                    "{} is not an attribute on the model",
                    "please implement a {} on the extract rule {}",
                )).format(field, extract_method, self)
                raise NotImplementedError(err_message)

            if not hasattr(self, get_field_description_method):
                err_message = " ".join(
                    "Please implement a {} message on the model",
                    "that returns a dictionary with 'display_name',",
                    "'description' and 'type_display_name'"
                )
                raise NotImplementedError(err_message)

    @property
    def file_name(self):
        """
        The file that will be extracted, not including the .csv
        """

        return "{}.csv".format(self.model.get_api_name())

    def get_base_field_dict(self):
        """
        A dictionary of episode id to fields that should exist
        in all csvs for that episode id.
        """
        fields = self.base_fields.keys()
        if "id" not in fields:
            fields = list(fields)
            fields.append("id")
        episode_qs = Episode.objects.filter(
            id__in=[i.id for i in self.episode_list]
        )
        values_list = episode_qs.values(*fields)
        result = {}
        for value_row in values_list:
            result[value_row["id"]] = {
                self.base_fields[k]: v for k, v in value_row.items()
            }
        return result

    def get_field_value(self, data):
        """
        Serialize a value from a model field to what appears in the csv
        """
        if isinstance(data, (list, dict,)):
            return json.dumps(data, cls=DjangoJSONEncoder)
        return str(data)

    def get_fields_name_to_display_name(self):
        """
        Return a dictionary of the instance field name to the display name
        """
        result = {}
        field_names = self.model._get_fieldnames_to_extract()
        fields_to_ignore = {
            "consistency_token", "episode_id", "patient_id", "id"
        }
        for field_name in field_names:
            if field_name in fields_to_ignore:
                continue
            result[field_name] = self.model._get_field_title(field_name)

        for field_name in self.additional_fields:
            description_getter = "get_{}_description".format(field_name)
            result[field_name] = getattr(self, description_getter)()["display_name"]

        return result

    def get_model_id_to_episode_ids(self):
        """
        Returns a list of dictionaries
        {id: [[ model_id]], 'episode_id': [[ episode_id]]}.

        Not that for a patient with multiple patient subrecords for the same type
        and multiple episodes we end up with a cartesian join ie multiple
        rows per episode and multiple rows per instance.

        e.g. Jane has two episodes, ICU(id 1) and Infection service (id 2)
        and two allergies, Aciclovir(id 3) and Amphotericin(id 4)

        the output for allergies will be

        [
            {'episode_id': 1, 'id': 3},
            {'episode_id': 2, 'id': 4},
            {'episode_id': 1, 'id': 3},
            {'episode_id': 2, 'id': 4},
        ]

        I am not sure this is necessarily correct
        """
        filter_arg = "{}__in".format(self.path_to_episode_id)
        list_of_dicts = self.model.objects.filter(
            **{
                filter_arg: [i.id for i in self.episode_list]
            }
        ).values('id', self.path_to_episode_id)
        result = defaultdict(list)
        for some_dict in list_of_dicts:
            result[some_dict["id"]].append(
                some_dict[self.path_to_episode_id]
            )
        return result

    def get_rows_for_instance(self, instance):
        """
        Get the rows that should appear in the csv for a given instance.
        This is the combination of the base fields that appear in
        every csv and the fields for the instance
        """
        episode_ids = self.model_id_to_episode_ids_dict[instance.id]
        model_row = self.get_instance_dict(instance)
        rows = []
        for episode_id in episode_ids:
            row = self.base_field_dict[episode_id].copy()
            row.update(model_row)
            rows.append(row)
        return rows

    def get_instance_dict(self, instance):
        """
        Return a serialized form of the instance without the base fields.
        """
        result = {}
        for field, display_name in self.model_field_name_to_display_name.items():
            getter = getattr(self, 'extract_{}'.format(field), None)
            if getter:
                value = getter(instance)
            else:
                value = self.get_field_value(getattr(instance, field))
            result[display_name] = value
        return result

    def get_rows(self):
        rows = []
        for instance in self.queryset:
            rows.extend(self.get_rows_for_instance(instance))
        return rows

    def sort_headers(self, headers):
        base_field_display_names = self.base_fields.values()
        return list(self.base_fields.values()) + [
            i for i in headers if i not in base_field_display_names
        ]

    def write_to_file(self, directory):
        """
        Writes what is generated out to a file
        """
        file_name = self.file_name
        full_file_name = os.path.join(directory, file_name)
        rows = self.get_rows()
        if not rows:
            return
        with open(full_file_name, "w") as f:
            fieldnames = self.sort_headers(rows[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        return file_name

    def get_field_description(self, field_name):
        get_method = "get_{}_description".format(
            field_name
        )
        if hasattr(self, get_method):
            return getattr(self, get_method)()
        return {
            "display_name": self.model._get_field_title(field_name),
            "description": self.model.get_field_description(field_name),
            "type_display_name": self.model.get_human_readable_type(field_name),
        }

    def get_data_dictionary(self):
        fields = self.model_field_name_to_display_name.keys()
        fields_descriptions = [
            self.get_field_description(field) for field in fields
        ]
        fields_descriptions = sorted(
            fields_descriptions, key=lambda x: x["display_name"]
        )
        display_name = getattr(self, "display_name", None)

        if not display_name:
            display_name = self.model.get_display_name()
        return {display_name: fields_descriptions}


class EpisodeRule(ModelRule):
    file_name = "episodes.csv"
    additional_fields = ["tagging"]
    display_name = "Episode"

    def __init__(self, episode_list, user):
        super().__init__(episode_list, user, Episode, "id")

    def get_tagging_description(self):
        return {
            "display_name": "Tagging",
            "description": "A list of tags that the episode has been tagged with",
            "type_display_name": "semicolon seperated list"
        }

    def extract_tagging(self, episode):
        return ";".join(
            episode.get_tag_names(self.user, historic=True)
        )
