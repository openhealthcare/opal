"""
Unittests for opal.core.search.extract
"""
import datetime
import json
from mock import mock_open, patch

from django.core.urlresolvers import reverse
from django.test import override_settings

from opal.core.test import OpalTestCase
from opal import models
from opal.tests.models import (
    Colour, PatientColour, Demographics, HatWearer, HouseOwner, FavouriteNumber
)
from opal.core.search import extract

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
        self.patient = models.Patient.objects.create()
        self.episode = models.Episode.objects.create(patient=self.patient)
        Demographics.objects.all().update(
            patient=self.patient,
            hospital_number='12345678',
            first_name="Alice",
            surname="Alderney",
            date_of_birth=datetime.date(1976,1,1)
        )
        super(PatientEpisodeTestCase, self).setUp()

    def mocked_extract(self, some_fun, args):
        m = mock_open()
        with patch(MOCKING_FILE_NAME_OPEN, m, create=True):
            some_fun(*args)

@patch('opal.core.search.extract.subrecords')
@patch('opal.core.search.extract.zipfile')
@patch('opal.core.search.extract.csv.writer')
class ZipFlatExtractTestCase(OpalTestCase):

    def test_write_headers(self, csv_writer, zipfile, subrecords):
        # write the display names of the fields
        patient, episode = self.new_patient_and_episode_please()
        subrecords.return_value = [HatWearer, HouseOwner]
        HatWearer.objects.create(name="Indiana", episode=episode)
        HatWearer.objects.create(name="Beryl", episode=episode)
        HouseOwner.objects.create(patient=patient)
        HouseOwner.objects.create(patient=patient)
        extract.zip_flat_extract(
            models.Episode.objects.all(), 'this', self.user
        )
        self.assertEqual(csv_writer().writerow.call_count, 2)
        headers_call = csv_writer().writerow.call_args_list[0][0][0]
        self.assertIn("Tagging", headers_call)
        self.assertIn("Start", headers_call)
        self.assertIn("End", headers_call)
        self.assertIn("Wearer of Hats-1 Name", headers_call)
        self.assertIn("Wearer of Hats-2 Name", headers_call)
        self.assertIn("House Owner-1 Created", headers_call)
        self.assertIn("House Owner-2 Created", headers_call)


    def test_exclude_empty_subrecords(self, csv_writer, zipfile, subrecords):
        # if a subrecord has no models, don't write the headers
        patient, episode = self.new_patient_and_episode_please()
        subrecords.return_value = [HatWearer, HouseOwner]
        HatWearer.objects.create(name="Indiana", episode=episode)
        HatWearer.objects.create(name="Beryl", episode=episode)
        extract.zip_flat_extract(
            models.Episode.objects.all(), 'this', self.user
        )
        self.assertEqual(csv_writer().writerow.call_count, 2)
        headers_call = csv_writer().writerow.call_args_list[0][0][0]
        self.assertIn("Tagging", headers_call)
        self.assertIn("Start", headers_call)
        self.assertIn("End", headers_call)
        self.assertIn("Wearer of Hats-1 Name", headers_call)
        self.assertIn("Wearer of Hats-2 Name", headers_call)
        self.assertNotIn("HouseOwner-1 Created", headers_call)

    def test_one_write_per_row(self, csv_writer, zipfile, subrecords):
        # if we've got multiple rows but they're all the same episode
        # only write one row
        patient, episode = self.new_patient_and_episode_please()
        subrecords.return_value = [HatWearer, FavouriteNumber]
        HatWearer.objects.create(name="Indiana", episode=episode)
        HatWearer.objects.create(name="Beryl", episode=episode)
        FavouriteNumber.objects.create(patient=patient, number=73)
        FavouriteNumber.objects.create(patient=patient, number=42)
        extract.zip_flat_extract(
            models.Episode.objects.all(), 'this', self.user
        )
        self.assertEqual(csv_writer().writerow.call_count, 2)
        row_call = csv_writer().writerow.call_args_list[1][0][0]
        self.assertIn("Beryl", row_call)
        self.assertIn("Indiana", row_call)
        self.assertIn("73", row_call)
        self.assertIn("42", row_call)


    def test_write_multiple_episode_subrecord_rows(self, csv_writer, zipfile, subrecords):
        # if we've got multiple rows but they're all the same episode
        # only write one row
        patient, episode_1 = self.new_patient_and_episode_please()
        episode_2 = patient.create_episode()
        subrecords.return_value = [HatWearer, FavouriteNumber]
        FavouriteNumber.objects.create(patient=patient, number=43)
        FavouriteNumber.objects.create(patient=patient, number=84)
        extract.zip_flat_extract(
            models.Episode.objects.all(), 'this', self.user
        )
        self.assertEqual(csv_writer().writerow.call_count, 3)
        row_call_1 = csv_writer().writerow.call_args_list[1][0][0]
        row_call_2 = csv_writer().writerow.call_args_list[2][0][0]
        self.assertIn("43", row_call_1)
        self.assertIn("84", row_call_1)
        self.assertIn("43", row_call_2)
        self.assertIn("84", row_call_2)

    def test_write_multiple_patient_subrecord_rows(self, csv_writer, zipfile, subrecords):
        patient, episode_1 = self.new_patient_and_episode_please()
        episode_2 = patient.create_episode()
        subrecords.return_value = [HatWearer, HouseOwner]
        HatWearer.objects.create(name="Indiana", episode=episode_1)
        HatWearer.objects.create(name="Beryl", episode=episode_2)
        extract.zip_flat_extract(
            models.Episode.objects.all(), 'this', self.user
        )
        self.assertEqual(csv_writer().writerow.call_count, 3)
        row_call_1 = csv_writer().writerow.call_args_list[1][0][0]
        row_call_2 = csv_writer().writerow.call_args_list[2][0][0]
        self.assertIn("Indiana", row_call_1)
        self.assertNotIn("Indiana", row_call_2)
        self.assertIn("Beryl", row_call_2)
        self.assertNotIn("Beryl", row_call_1)

    def test_exclude_from_extract(self, csv_writer, zipfile, subrecords):
        patient, episode = self.new_patient_and_episode_please()
        subrecords.return_value = [HatWearer, Colour]
        Colour.objects.create(name="Blue", episode=episode)
        HatWearer.objects.create(name="Indiana", episode=episode)
        extract.zip_flat_extract(
            models.Episode.objects.all(), 'this', self.user
        )
        self.assertEqual(csv_writer().writerow.call_count, 2)
        headers = csv_writer().writerow.call_args_list[0][0][0]
        self.assertNotIn("{}-1 Name".format(Colour.get_display_name()), headers)

        row_call = csv_writer().writerow.call_args_list[1][0][0]
        self.assertNotIn("Blue", row_call)

    def test_doesnt_fail_if_empty_extract(self, csv_writer, zipfile, subrecords):
        subrecords.return_value = [HatWearer]
        extract.zip_flat_extract(
            models.Episode.objects.all(), 'this', self.user
        )
        self.assertEqual(csv_writer().writerow.call_count, 1)
        headers_call = csv_writer().writerow.call_args_list[0][0][0]
        self.assertIn("Tagging", headers_call)

    def test_specific_columns_excludes_other_records(self, csv_writer, zipfile, subrecords):
        # if we don't pass in houseowner and we do pass in
        # hatwearer, then we should only see hatwearer
        patient, episode = self.new_patient_and_episode_please()
        subrecords.return_value = [HatWearer, HouseOwner]
        HatWearer.objects.create(name="Indiana", episode=episode)
        HouseOwner.objects.create(patient=patient)
        extract.zip_flat_extract(
            models.Episode.objects.all(), 'this', self.user,
            specific_columns={HatWearer.get_api_name(): None}
        )
        self.assertEqual(csv_writer().writerow.call_count, 2)
        headers_call = csv_writer().writerow.call_args_list[0][0][0]
        self.assertNotIn("Tagging", headers_call)
        self.assertIn("Wearer of Hats-1 Name", headers_call)
        self.assertNotIn("House Owner-1 Created", headers_call)

    def test_use_episode_columns_if_passed_in(self, csv_writer, zipfile, subrecords):
        patient, episode = self.new_patient_and_episode_please()
        subrecords.return_value = [HatWearer, HouseOwner]
        HatWearer.objects.create(name="Indiana", episode=episode)
        HouseOwner.objects.create(patient=patient)
        extract.zip_flat_extract(
            models.Episode.objects.all(), 'this', self.user,
            specific_columns={"episode": ["tagging"]}
        )
        self.assertEqual(csv_writer().writerow.call_count, 2)
        headers_call = csv_writer().writerow.call_args_list[0][0][0]
        self.assertEqual(
            ['ID', 'Patient', 'Tagging'],
            headers_call
        )

    def test_only_use_specifc_subrecords(self, csv_writer, zipfile, subrecords):
        patient, episode = self.new_patient_and_episode_please()
        subrecords.return_value = [HatWearer, HouseOwner]
        HatWearer.objects.create(name="Indiana", episode=episode)
        HouseOwner.objects.create(patient=patient)
        extract.zip_flat_extract(
            models.Episode.objects.all(), 'this', self.user,
            specific_columns={"episode": ["tagging"]}
        )
        self.assertEqual(csv_writer().writerow.call_count, 2)
        headers_call = csv_writer().writerow.call_args_list[0][0][0]
        self.assertEqual(
            ['ID', 'Patient', 'Tagging'],
            headers_call
        )

    def test_if_none_show_all_fields_subrecord(self, csv_writer, zipfile, subrecords):
        patient, episode = self.new_patient_and_episode_please()
        subrecords.return_value = [HatWearer, HouseOwner]
        HatWearer.objects.create(name="Indiana", episode=episode)
        Colour.objects.create(name="red", episode=episode)

        with patch.object(HatWearer, "_get_fieldnames_to_extract") as field_names:
            field_names.return_value = [
                "id", "created", "name", "consistency_token"
            ]

            extract.zip_flat_extract(
                models.Episode.objects.all(), 'this', self.user,
                specific_columns={"hat_wearer": None}
            )
        self.assertEqual(csv_writer().writerow.call_count, 2)
        headers_call = csv_writer().writerow.call_args_list[0][0][0]
        self.assertEqual(
            [
                'Patient',
                'ID',
                'Wearer of Hats-1 Created',
                'Wearer of Hats-1 Name'
            ],
            headers_call
        )


@patch('opal.core.search.extract.subrecords')
@patch('opal.core.search.extract.zipfile')
class ZipNestedExtractTestCase(OpalTestCase):

    def test_subrecords(self, zipfile, subrecords):
        patient, episode = self.new_patient_and_episode_please()
        subrecords.return_value = [HatWearer, HouseOwner]
        HatWearer.objects.create(name="Indiana", episode=episode)
        HouseOwner.objects.create(patient=patient)
        extract.zip_nested_extract(models.Episode.objects.all(), 'this', self.user)
        call_args = zipfile.ZipFile.return_value.__enter__.return_value.write.call_args_list
        self.assertEqual(3, len(call_args))
        self.assertTrue(call_args[0][0][0].endswith("episodes.csv"))
        self.assertTrue(call_args[1][0][0].endswith("hat_wearer.csv"))
        self.assertTrue(call_args[2][0][0].endswith("house_owner.csv"))

    def test_subrecords_if_none(self, zipfile, subrecords):
        # if there are no subrecords we don't expect them to write to the file
        patient, episode = self.new_patient_and_episode_please()
        subrecords.return_value = [HatWearer, HouseOwner]
        HouseOwner.objects.create(patient=patient)
        extract.zip_nested_extract(models.Episode.objects.all(), 'this', self.user)
        call_args = zipfile.ZipFile.return_value.__enter__.return_value.write.call_args_list
        self.assertEqual(2, len(call_args))
        self.assertTrue(call_args[0][0][0].endswith("episodes.csv"))
        self.assertTrue(call_args[1][0][0].endswith("house_owner.csv"))

    def test_subrecords_if_empty_query(self, zipfile, subrecords):
        # if there are no subrecords we don't expect them to write to the file
        subrecords.return_value = [HatWearer, HouseOwner]
        extract.zip_nested_extract(models.Episode.objects.all(), 'this', self.user)
        call_args = zipfile.ZipFile.return_value.__enter__.return_value.write.call_args_list
        self.assertEqual(1, len(call_args))
        self.assertTrue(call_args[0][0][0].endswith("episodes.csv"))

    @patch('opal.core.search.extract.EpisodeCsvRenderer')
    def test_exclude_subrecords(self, csv_renderer, zipfile,  subrecords):
        # if the subrecord is marked as _exclude_from_extract, skip it
        subrecords.return_value = [Colour]
        extract.zip_nested_extract(models.Episode.objects.all(), 'this', self.user)
        self.assertEqual(csv_renderer.call_count, 1)
        self.assertEqual(csv_renderer.call_args[0][0], models.Episode)


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
        self.assertIn("trees;leaves", renderer.get_row(self.episode))


@patch.object(PatientColour, "_get_fieldnames_to_extract")
class TestPatientSubrecordCsvRenderer(OpalTestCase):

    def test_get_header(self, field_names_to_extract):
        field_names_to_extract.return_value = [
            "patient_id", "name", "consistency_token", "id"
        ]
        renderer = extract.PatientSubrecordCsvRenderer(
            PatientColour,
            models.Episode.objects.all(),
            self.user
        )
        self.assertEqual(
            ["Episode", "Patient", "Name"], renderer.get_headers()
        )

    def test_get_row(self, field_names_to_extract):
        field_names_to_extract.return_value = [
            "patient_id", "name", "consistency_token", "id"
        ]
        patient, episode = self.new_patient_and_episode_please()
        patient_colour = PatientColour.objects.create(
            name="blue", patient=patient
        )
        renderer = extract.PatientSubrecordCsvRenderer(
            PatientColour,
            models.Episode.objects.all(),
            self.user
        )
        rendered = renderer.get_row(patient_colour, episode.id)
        self.assertEqual(["1", "1", "blue"], rendered)

    def test_get_rows(self, field_names_to_extract):
        field_names_to_extract.return_value = [
            "patient_id", "name", "consistency_token", "id"]
        patient, _ = self.new_patient_and_episode_please()
        PatientColour.objects.create(
            name="blue", patient=patient
        )
        renderer = extract.PatientSubrecordCsvRenderer(
            PatientColour,
            models.Episode.objects.all(),
            self.user
        )
        rendered = list(
            renderer.get_rows()
        )
        PatientColour.objects.create(
            name="blue", patient=patient
        )
        self.assertEqual([["1", "1", "blue"]], rendered)

    def test_get_rows_same_patient(self, field_names_to_extract):
        patient, _ = self.new_patient_and_episode_please()
        patient.create_episode()
        field_names_to_extract.return_value = [
            "patient_id", "name", "consistency_token", "id"
        ]
        patient, _ = self.new_patient_and_episode_please()
        PatientColour.objects.create(
            name="blue", patient=patient
        )

        renderer = extract.PatientSubrecordCsvRenderer(
            PatientColour,
            models.Episode.objects.all(),
            self.user
        )
        rendered = list(
            renderer.get_rows()
        )
        self.assertEqual([
            ["1", "1", "blue"],
            ["2", "1", "blue"]
        ], rendered)

    def test_get_flat_headers(self, field_names_to_extract):
        field_names_to_extract.return_value = [
            "name", "consistency_token", "id"
        ]
        patient_1, _ = self.new_patient_and_episode_please()
        patient_2, _ = self.new_patient_and_episode_please()
        PatientColour.objects.create(name="red", patient=patient_1)
        PatientColour.objects.create(name="purple", patient=patient_2)
        PatientColour.objects.create(name="green", patient=patient_2)
        renderer = extract.PatientSubrecordCsvRenderer(
            PatientColour, models.Episode.objects.all(), self.user, flat=True
        )
        expected = [
            'Patient Colour-1 Name',
            'Patient Colour-2 Name'
        ]
        self.assertEqual(renderer.get_flat_headers(), expected)

    def test_get_flat_row_by_episode_id(self, field_names_to_extract):
        field_names_to_extract.return_value = [
            "name", "consistency_token", "id"
        ]
        patient_1, episode_1 = self.new_patient_and_episode_please()
        patient_2, episode_2 = self.new_patient_and_episode_please()
        PatientColour.objects.create(name="red", patient=patient_1)
        PatientColour.objects.create(name="purple", patient=patient_2)
        PatientColour.objects.create(name="green", patient=patient_2)
        renderer = extract.PatientSubrecordCsvRenderer(
            PatientColour, models.Episode.objects.all(), self.user, flat=True
        )
        row_1 = renderer.get_flat_row_for_episode_id(episode_1.id)
        self.assertEqual(
            row_1,
            ["red", ""]
        )
        row_2 = renderer.get_flat_row_for_episode_id(episode_2.id)
        self.assertEqual(
            row_2,
            ["purple", "green"]
        )


@patch.object(Colour, "_get_fieldnames_to_extract")
class TestEpisodeSubrecordCsvRenderer(OpalTestCase):

    def test_get_flat_headers(self, field_names_to_extract):
        field_names_to_extract.return_value = [
            "episode_id", "name", "consistency_token", "id"
        ]
        _, episode_1 = self.new_patient_and_episode_please()
        _, episode_2 = self.new_patient_and_episode_please()
        Colour.objects.create(name="red", episode=episode_1)
        Colour.objects.create(name="purple", episode=episode_2)
        Colour.objects.create(name="green", episode=episode_2)
        renderer = extract.EpisodeSubrecordCsvRenderer(
            Colour, models.Episode.objects.all(), self.user, flat=True
        )
        expected = [
            'Colour-1 Name',
            'Colour-2 Name'
        ]
        self.assertEqual(renderer.get_flat_headers(), expected)

    def test_get_flat_row_by_episode_id(self, field_names_to_extract):
        field_names_to_extract.return_value = [
            "name", "consistency_token", "id"
        ]
        _, episode_1 = self.new_patient_and_episode_please()
        _, episode_2 = self.new_patient_and_episode_please()
        Colour.objects.create(name="red", episode=episode_1)
        Colour.objects.create(name="purple", episode=episode_2)
        Colour.objects.create(name="green", episode=episode_2)
        renderer = extract.EpisodeSubrecordCsvRenderer(
            Colour, models.Episode.objects.all(), self.user, flat=True
        )
        row_1 = renderer.get_flat_row_for_episode_id(episode_1.id)
        self.assertEqual(
            row_1,
            ["red", ""]
        )
        row_2 = renderer.get_flat_row_for_episode_id(episode_2.id)
        self.assertEqual(
            row_2,
            ["purple", "green"]
        )

    def test_get_flat_row_by_episode_id_where_none_exists(
        self, field_names_to_extract
    ):
        field_names_to_extract.return_value = [
            "episode_id", "name", "consistency_token", "id"
        ]
        _, episode_1 = self.new_patient_and_episode_please()
        _, episode_2 = self.new_patient_and_episode_please()
        Colour.objects.create(name="purple", episode=episode_2)
        Colour.objects.create(name="green", episode=episode_2)
        renderer = extract.EpisodeSubrecordCsvRenderer(
            Colour, models.Episode.objects.all(), self.user, flat=True
        )
        row_1 = renderer.get_flat_row_for_episode_id(episode_1.id)
        self.assertEqual(
            row_1,
            ["", ""]
        )
        row_2 = renderer.get_flat_row_for_episode_id(episode_2.id)
        self.assertEqual(
            row_2,
            ["purple","green"]
        )

    def test_get_header(self, field_names_to_extract):
        _, episode = self.new_patient_and_episode_please()

        field_names_to_extract.return_value = [
            "episode_id", "name", "consistency_token", "id"
        ]
        renderer = extract.EpisodeSubrecordCsvRenderer(
            Colour,
            models.Episode.objects.all(),
            self.user
        )
        self.assertEqual(
            ["Patient", "Episode", "Name"], renderer.get_headers()
        )

    def test_get_row(self, field_names_to_extract):
        _, episode = self.new_patient_and_episode_please()
        colour = Colour.objects.create(
            name="blue", episode=episode
        )
        field_names_to_extract.return_value = [
            "episode_id", "name", "consistency_token", "id"
        ]
        renderer = extract.EpisodeSubrecordCsvRenderer(
            Colour, models.Episode.objects.all(), self.user
        )
        rendered = renderer.get_row(colour)
        self.assertEqual(["1", "1", "blue"], rendered)
