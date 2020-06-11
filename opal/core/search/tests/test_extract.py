"""
Unittests for opal.core.search.extract
"""
import datetime
import json
import os

from django.urls import reverse
from django.test import override_settings
from django.utils import timezone
from unittest.mock import mock_open, patch, Mock, MagicMock

from opal.core.test import OpalTestCase
from opal import models
from opal.tests.models import (
    Colour, PatientColour, Demographics, HatWearer, HouseOwner
)
from opal.core.search import extract
from six import u


MOCKING_FILE_NAME_OPEN = "opal.core.search.extract.open"


class TestViewPOSTTestCase(OpalTestCase):

    def test_check_view(self):
        # a vanilla check to make sure that the view returns a zip file
        url = reverse("extract_download")
        post_data = {
            "criteria":
                json.dumps([{
                    "combine": "and",
                    "column": "demographics",
                    "field": "Surname",
                    "queryType": "Contains",
                    "query": "a",
                    "lookup_list": [],
                }])
        }

        self.assertTrue(
            self.client.login(username=self.user.username, password=self.PASSWORD)
        )

        response = self.client.post(url, post_data)

        self.assertEqual(response.status_code, 200)

    @override_settings(EXTRACT_ASYNC=True)
    def test_check_view_with_sync_extract(self):
        url = reverse("extract_download")
        post_data = {
            "criteria":
                   json.dumps([{
                    "combine": "and",
                    "column": "demographics",
                    "field": "Surname",
                    "queryType": "Contains",
                    "query": "a",
                    "lookup_list": [],
                }])
        }

        self.assertTrue(
            self.client.login(username=self.user.username, password=self.PASSWORD)
        )

        response = self.client.post(url, json.dumps(post_data), content_type='appliaction/json')
        self.assertEqual(response.status_code, 200)


class PatientEpisodeTestCase(OpalTestCase):
    def setUp(self):
        self.patient, self.episode = self.new_patient_and_episode_please()
        Demographics.objects.all().update(
            patient=self.patient,
            hospital_number='12345678',
            first_name="Alice",
            surname="Alderney",
            date_of_birth=datetime.date(1976, 1, 1)
        )
        super(PatientEpisodeTestCase, self).setUp()

    def mocked_extract(self, some_fun, args):
        m = mock_open()
        with patch(MOCKING_FILE_NAME_OPEN, m, create=True):
            some_fun(*args)


class GenerateFilesTestCase(OpalTestCase):
    @patch('opal.core.search.extract.subrecords')
    @patch('opal.core.search.extract.CsvRenderer.write_to_file')
    @patch('opal.core.search.extract.write_data_dictionary')
    def test_generate_csv_files(
        self, write_data_dictionary, write_to_file, subrecords
    ):
        patient, episode = self.new_patient_and_episode_please()
        subrecords.return_value = [HatWearer, HouseOwner]
        HatWearer.objects.create(name="Indiana", episode=episode)
        HouseOwner.objects.create(patient=patient)
        results = extract.generate_csv_files(
            "somewhere", models.Episode.objects.all(), self.user
        )
        expected = [
            (os.path.join('somewhere', 'data_dictionary.html'), 'data_dictionary.html'),
            (os.path.join('somewhere', 'episodes.csv'), 'episodes.csv'),
            (os.path.join('somewhere', 'hat_wearer.csv'), 'hat_wearer.csv'),
            (os.path.join('somewhere', 'house_owner.csv'), 'house_owner.csv')
        ]
        self.assertEqual(expected, results)
        self.assertEqual(
            write_data_dictionary.call_args[0][0],
            os.path.join('somewhere', 'data_dictionary.html'),
        )
        self.assertEqual(
            write_to_file.call_args[0], (os.path.join('somewhere', 'house_owner.csv'),)
        )

    @patch('opal.core.search.extract.subrecords')
    @patch('opal.core.search.extract.EpisodeSubrecordCsvRenderer')
    @patch('opal.core.search.extract.CsvRenderer.write_to_file')
    @patch('opal.core.search.extract.write_data_dictionary')
    def test_exclude_subrecords(
        self, write_data_dictionary, write_to_file, csv_renderer, subrecords
    ):
        subrecords.return_value = [Colour]
        extract.generate_csv_files(
            "somewhere", models.Episode.objects.all(), self.user
        )
        self.assertEqual(csv_renderer.call_count, 0)


class ZipArchiveTestCase(OpalTestCase):

    @patch('opal.core.search.extract.subrecords')
    @patch('opal.core.search.extract.zipfile')
    def test_subrecords(self, zipfile, subrecords):
        patient, episode = self.new_patient_and_episode_please()
        subrecords.return_value = [HatWearer, HouseOwner]
        HatWearer.objects.create(name="Indiana", episode=episode)
        HouseOwner.objects.create(patient=patient)
        extract.zip_archive(models.Episode.objects.all(), 'this', self.user)
        call_args = zipfile.ZipFile.return_value.__enter__.return_value.write.call_args_list
        self.assertEqual(4, len(call_args))
        self.assertTrue(call_args[0][0][0].endswith("data_dictionary.html"))
        self.assertTrue(call_args[1][0][0].endswith("episodes.csv"))
        self.assertTrue(call_args[2][0][0].endswith("hat_wearer.csv"))
        self.assertTrue(call_args[3][0][0].endswith("house_owner.csv"))

    @patch('opal.core.search.extract.subrecords')
    @patch('opal.core.search.extract.zipfile')
    def test_subrecords_if_none(self, zipfile, subrecords):
        # if there are no subrecords we don't expect them to write to the file
        patient, episode = self.new_patient_and_episode_please()
        subrecords.return_value = [HatWearer, HouseOwner]
        HouseOwner.objects.create(patient=patient)
        extract.zip_archive(models.Episode.objects.all(), 'this', self.user)
        call_args = zipfile.ZipFile.return_value.__enter__.return_value.write.call_args_list
        self.assertEqual(3, len(call_args))
        self.assertTrue(call_args[0][0][0].endswith("data_dictionary.html"))
        self.assertTrue(call_args[1][0][0].endswith("episodes.csv"))
        self.assertTrue(call_args[2][0][0].endswith("house_owner.csv"))

    @patch('opal.core.search.extract.subrecords')
    @patch('opal.core.search.extract.zipfile')
    def test_subrecords_if_empty_query(self, zipfile, subrecords):
        # if there are no subrecords we don't expect them to write to the file
        subrecords.return_value = [HatWearer, HouseOwner]
        extract.zip_archive(models.Episode.objects.all(), 'this', self.user)
        call_args = zipfile.ZipFile.return_value.__enter__.return_value.write.call_args_list
        self.assertEqual(2, len(call_args))
        self.assertTrue(call_args[0][0][0].endswith("data_dictionary.html"))
        self.assertTrue(call_args[1][0][0].endswith("episodes.csv"))


class AsyncExtractTestCase(OpalTestCase):

    @patch('opal.core.search.tasks.extract.delay')
    def test_async(self, delay):
        extract.async_extract(self.user, 'THIS')
        delay.assert_called_with(self.user, 'THIS')


class TestBasicCsvRenderer(PatientEpisodeTestCase):
    def test_init(self):
        renderer = extract.CsvRenderer(Colour, Colour.objects.all(), self.user)
        self.assertEqual(renderer.model, Colour)
        renderer = extract.CsvRenderer(Colour, Colour.objects.all(), self.user)
        self.assertEqual(renderer.fields, renderer.get_field_names_to_render())

    def test_0_count(self):
        renderer = extract.CsvRenderer(Colour, Colour.objects.all(), self.user)
        self.assertEqual(renderer.count(), 0)

    def test_1_count(self):
        Colour.objects.create(name="Blue", episode=self.episode)
        renderer = extract.CsvRenderer(Colour, Colour.objects.all(), self.user)
        self.assertEqual(renderer.count(), 1)

    def test_set_fields(self):
        renderer = extract.CsvRenderer(Colour, Colour.objects.all(), self.user, fields=[
            "name", "episode_id"
        ])
        self.assertEqual(renderer.fields, ["name", "episode_id"])
        self.assertEqual(
            renderer.get_headers(),
            ["Name", "Episode"]
        )

    def test_get_field_names_to_render(self):
        with patch.object(Colour, "_get_fieldnames_to_extract") as field_names:
            field_names.return_value = ["name", "consistency_token"]
            renderer = extract.CsvRenderer(
                Colour,  Colour.objects.all(), self.user
            )
            self.assertEqual(
                renderer.fields,
                ["name"]
            )

    def test_fields_uses_fields_arg(self):
            renderer = extract.CsvRenderer(
                Colour,  Colour.objects.all(), self.user, fields=["name"]
            )
            self.assertEqual(
                renderer.fields,
                ["name"]
            )

    def test_get_headers(self):
        with patch.object(Colour, "_get_fieldnames_to_extract") as field_names:
            field_names.return_value = ["name", "consistency_token"]
            renderer = extract.CsvRenderer(
                Colour, Colour.objects.all(), self.user
            )
            self.assertEqual(
                renderer.get_headers(),
                ["Name"]
            )

    def test_get_headers_uses_fields_arg(self):
        renderer = extract.CsvRenderer(
            Colour,  Colour.objects.all(), self.user, fields=["name"]
        )
        self.assertEqual(
            renderer.get_headers(),
            ["Name"]
        )

    def test_serialize_list_simple(self):
        renderer = extract.CsvRenderer(
            Colour,  Colour.objects.all(), self.user, fields=["name"]
        )
        result = renderer.serialize_value(["hello", "there"])
        self.assertEqual(
            result,
            "hello; there"
        )

    def test_serialize_list_complex(self):
        renderer = extract.CsvRenderer(
            Colour,  Colour.objects.all(), self.user, fields=["name"]
        )

        dt = timezone.make_aware(datetime.datetime(2017, 2, 9, 10, 00, 16))
        result = renderer.serialize_value([{"hello": dt}])
        self.assertEqual(
            result,
            '[{"hello": "2017-02-09T10:00:16Z"}]'
        )

    def test_serialize_dict(self):
        renderer = extract.CsvRenderer(
            Colour,  Colour.objects.all(), self.user, fields=["name"]
        )

        dt = timezone.make_aware(datetime.datetime(2017, 2, 9, 10, 00, 16))
        result = renderer.serialize_value({"hello": dt})
        self.assertEqual(
            result,
            '{"hello": "2017-02-09T10:00:16Z"}'
        )

    def test_serialize_number(self):
        renderer = extract.CsvRenderer(
            Colour,  Colour.objects.all(), self.user, fields=["name"]
        )

        result = renderer.serialize_value(1)
        self.assertEqual(result, "1")

    def test_serialize_string(self):
        renderer = extract.CsvRenderer(
            Colour,  Colour.objects.all(), self.user, fields=["name"]
        )
        result = renderer.serialize_value("hello")
        self.assertEqual(result, "hello")

    def test_list_render(self):
        _, episode = self.new_patient_and_episode_please()
        colour = Colour.objects.create(name="Blue", episode=episode)
        normal_to_dict = colour.to_dict(self.user)
        normal_to_dict["name"] = ["onions", "kettles"]
        with patch.object(colour, "to_dict") as to_dicted:
            to_dicted.return_value = normal_to_dict
            renderer = extract.CsvRenderer(
                Colour, Colour.objects.all(), self.user
            )
            result = renderer.get_row(colour)
            self.assertIn("onions; kettles", result)

    def test_to_dict_render(self):
        _, episode = self.new_patient_and_episode_please()
        colour = Colour.objects.create(name="Blue", episode=episode)
        normal_to_dict = colour.to_dict(self.user)
        normal_to_dict["name"] = {"RGB": "50, 168, 82", "Hex": "#32a852"}
        with patch.object(colour, "to_dict") as to_dicted:
            to_dicted.return_value = normal_to_dict
            renderer = extract.CsvRenderer(
                Colour, Colour.objects.all(), self.user
            )
            result = renderer.get_row(colour)
            self.assertIn(json.dumps(normal_to_dict["name"]), result)

    def test_get_row(self):
        with patch.object(Colour, "_get_fieldnames_to_extract") as field_names:
            _, episode = self.new_patient_and_episode_please()
            colour = Colour.objects.create(name="Blue", episode=episode)
            field_names.return_value = ["name", "consistency_token"]
            renderer = extract.CsvRenderer(
                Colour, Colour.objects.all(), self.user
            )
            self.assertEqual(
                renderer.get_row(colour),
                ["Blue"]
            )

    def test_get_row_uses_fields_arg(self):
        _, episode = self.new_patient_and_episode_please()
        colour = Colour.objects.create(name="Blue", episode=episode)
        renderer = extract.CsvRenderer(
            Colour,  Colour.objects.all(), self.user, fields=["name"]
        )
        self.assertEqual(
            renderer.get_row(colour),
            ["Blue"]
        )

    def test_get_rows(self):
        _, episode = self.new_patient_and_episode_please()
        colour = Colour.objects.create(name="Blue", episode=episode)
        renderer = extract.CsvRenderer(
            Colour, Colour.objects.all(), self.user
        )
        with patch.object(renderer, "get_row") as get_row:
            get_row.return_value = ["some_row"]
            result = list(renderer.get_rows())

        get_row.assert_called_with(colour)
        self.assertEqual(result, [["some_row"]])

    @patch("opal.core.search.extract.csv")
    def test_write_to_file(self, csv):
        _, episode = self.new_patient_and_episode_please()
        Colour.objects.create(name="Blue", episode=episode)
        renderer = extract.CsvRenderer(
            Colour, Colour.objects.all(), self.user
        )
        with patch.object(renderer, "get_rows"):
            with patch.object(renderer, "get_headers"):
                renderer.get_rows.return_value = [["row"]]
                renderer.get_headers.return_value = ["header"]
                self.mocked_extract(renderer.write_to_file, ["some file"])
                self.assertEqual(renderer.get_rows.call_count, 1)
                self.assertEqual(renderer.get_headers.call_count, 1)
                self.assertEqual(csv.writer().writerow.call_count, 2)
                self.assertEqual(csv.writer().writerow.mock_calls[0][1][0], ["header"])
                self.assertEqual(csv.writer().writerow.mock_calls[1][1][0], ["row"])


class TestEpisodeCsvRenderer(PatientEpisodeTestCase):

    def test_init(self):
        renderer = extract.EpisodeCsvRenderer(
            models.Episode,
            models.Episode.objects.all(),
            self.user
        )
        self.assertEqual(renderer.model, models.Episode)

    def test_headers(self):
        expected = {
            "Start",
            "End",
            "Created",
            "Updated",
            "Created By",
            "Updated By",
            "Patient",
            "Tagging"
        }
        renderer = extract.EpisodeCsvRenderer(
            models.Episode,
            models.Episode.objects.all(),
            self.user
        )
        self.assertEqual(len(expected - set(renderer.get_headers())), 0)

    def test_get_row(self):
        renderer = extract.EpisodeCsvRenderer(
            models.Episode,
            models.Episode.objects.all(),
            self.user
        )
        self.episode.set_tag_names(["trees"], self.user)
        # make sure we keep historic tags
        self.episode.set_tag_names(["leaves"], self.user)
        row = renderer.get_row(self.episode)
        self.assertTrue(
            "trees;leaves" in row or "leaves;trees" in row
        )


@patch.object(PatientColour, "_get_fieldnames_to_extract")
class TestPatientSubrecordCsvRenderer(PatientEpisodeTestCase):

    def setUp(self):
        self.patient, self.episode = self.new_patient_and_episode_please()
        self.patient_colour = PatientColour.objects.create(
            name="blue", patient=self.patient
        )
        self.pid_str = str(self.patient.id)
        self.eid_str = str(self.episode.id)

    def test_get_header(self, field_names_to_extract):
        field_names_to_extract.return_value = [
            "patient_id", "name", "consistency_token", "id"
        ]
        renderer = extract.PatientSubrecordCsvRenderer(
            PatientColour,
            models.Episode.objects.all(),
            self.user
        )
        self.assertEqual(["Episode", "Patient", "Name"], renderer.get_headers())

    def test_get_row(self, field_names_to_extract):
        field_names_to_extract.return_value = [
            "patient_id", "name", "consistency_token", "id"
        ]
        renderer = extract.PatientSubrecordCsvRenderer(
            PatientColour,
            models.Episode.objects.all(),
            self.user
        )
        rendered = renderer.get_row(self.patient_colour, self.episode.id)
        self.assertEqual(
            [str(self.episode.id), str(self.patient.id), "blue"], rendered
        )

    def test_get_rows(self, field_names_to_extract):
        field_names_to_extract.return_value = [
            "patient_id", "name", "consistency_token", "id"
        ]
        renderer = extract.PatientSubrecordCsvRenderer(
            PatientColour,
            models.Episode.objects.all(),
            self.user
        )
        rendered = list(
            renderer.get_rows()
        )
        expected = [[self.eid_str, self.pid_str, "blue"]]
        self.assertEqual(expected, rendered)

    def test_get_rows_same_patient(self, field_names_to_extract):
        self.patient.create_episode()
        first_episode = self.patient.episode_set.first()
        last_episode = self.patient.episode_set.last()
        field_names_to_extract.return_value = [
            "patient_id", "name", "consistency_token", "id"
        ]

        renderer = extract.PatientSubrecordCsvRenderer(
            PatientColour,
            models.Episode.objects.all(),
            self.user
        )
        rendered = list(
            renderer.get_rows()
        )
        self.assertEqual([
            [str(first_episode.id), str(self.patient.id), "blue"],
            [str(last_episode.id), str(self.patient.id), "blue"]
        ], rendered)


@patch.object(Colour, "_get_fieldnames_to_extract")
class TestEpisodeSubrecordCsvRenderer(PatientEpisodeTestCase):
    def setUp(self):
        self.patient, self.episode = self.new_patient_and_episode_please()
        self.colour = Colour.objects.create(
            name="blue", episode=self.episode
        )
        self.eid_str = str(self.episode.id)
        self.pid_str = str(self.patient.id)

    def test_get_header(self, field_names_to_extract):
        field_names_to_extract.return_value = [
            "episode_id", "name", "consistency_token", "id"
        ]
        renderer = extract.EpisodeSubrecordCsvRenderer(
            Colour,
            models.Episode.objects.all(),
            self.user
        )
        self.assertEqual(["Patient", "Episode", "Name"], renderer.get_headers())

    def test_get_row(self, field_names_to_extract):
        field_names_to_extract.return_value = [
            "episode_id", "name", "consistency_token", "id"
        ]
        renderer = extract.EpisodeSubrecordCsvRenderer(
            Colour, models.Episode.objects.all(), self.user
        )
        rendered = renderer.get_row(self.colour)
        expected = [self.pid_str, self.eid_str, "blue"]
        self.assertEqual(expected, rendered)


@patch('opal.core.search.extract.subrecords')
class GetDataDictionaryTestCase(OpalTestCase):
    def test_excludes_from_data_dictionary(self, subrecords):
        subrecords.return_value = [Colour]
        result = extract.get_data_dictionary()
        result.pop('Episode')
        # without result we should be empty
        self.assertFalse(bool(result))

    def test_episode_data_dictionary(self, subrecords):
        subrecords.return_value = []
        dd = extract.get_data_dictionary()
        episode = dd.pop('Episode')
        start = next(i for i in episode if i["display_name"] == 'Start')
        self.assertEqual(
            start['type_display_name'], 'Date'
        )

    def test_subrecord_data_dictionary(self, subrecords):
        subrecords.return_value = [HatWearer]
        dd = extract.get_data_dictionary()
        hat_wearer = dd.pop(HatWearer.get_display_name())
        hats = next(i for i in hat_wearer if i["display_name"] == 'Hats')
        self.assertEqual(
            hats['type_display_name'], 'Some of the Hats'
        )
        wearing_a_hat = next(
            i for i in hat_wearer if i["display_name"] == 'Wearing A Hat'
        )
        self.assertEqual(
            wearing_a_hat['type_display_name'], 'Either True or False'
        )
