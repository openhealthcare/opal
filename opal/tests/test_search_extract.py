"""
Unittests for opal.core.search.extract
"""
import datetime
import json
from mock import mock_open, Mock, patch

from django.core.urlresolvers import reverse
from django.test import override_settings

from opal.core.test import OpalTestCase
from opal import models
from opal.tests.models import (
    Colour, PatientColour, Demographics, HatWearer, HouseOwner
)
from opal.core.search import extract
from opal.core import subrecords
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


class SubrecordCSVTestCase(PatientEpisodeTestCase):

    @patch("opal.core.search.extract.csv")
    def test_no_episodes(self, csv):
        csv.writer = Mock()
        file_name = "fake file name"

        self.mocked_extract(
            extract.episode_subrecord_csv,
            [[], Colour, file_name]
        )
        headers = csv.writer().writerow.call_args_list[0][0][0]
        self.assertEqual(csv.writer().writerow.call_count, 1)
        expected_headers = [
            'patient_id',
            'created',
            'updated',
            'created_by_id',
            'updated_by_id',
            'episode_id',
            'name'
        ]
        self.assertEqual(headers, expected_headers)

    @patch("opal.core.search.extract.csv")
    def test_with_subrecords(self, csv):
        csv.writer = Mock()
        file_name = "fake file name"
        colour = Colour.objects.create(episode=self.episode, name='blue')

        self.mocked_extract(
            extract.episode_subrecord_csv,
            [[self.episode], Colour, file_name]
        )

        headers = csv.writer().writerow.call_args_list[0][0][0]
        row = csv.writer().writerow.call_args_list[1][0][0]
        expected_headers = [
            'patient_id',
            'created',
            'updated',
            'created_by_id',
            'updated_by_id',
            'episode_id',
            'name'
        ]
        expected_row = [
            "1", 'None', 'None', 'None', 'None', str(self.episode.id), u'blue'
        ]
        self.assertEqual(headers, expected_headers)
        self.assertEqual(row, expected_row)


class EpisodeCSVTestCase(PatientEpisodeTestCase):

    @patch('opal.core.search.extract.csv')
    def test_uses_fieldnames_to_extract(self, csv):
        with patch.object(extract.Episode, '_get_fieldnames_to_extract') as extractor:
            extractor.return_value = ['start', 'end', 'consistency_token']
            self.mocked_extract(
                extract.episode_csv,
                [[self.episode], self.user, 'fake file name']
            )
            headers = csv.writer().writerow.call_args_list[0][0][0]
            self.assertEqual(['tagging', 'start', 'end'], headers)


class PatientSubrecordCSVTestCase(PatientEpisodeTestCase):

    @patch("opal.core.search.extract.csv")
    def test_strips_pid(self, csv):
        csv.writer = Mock()
        file_name = "fake file name"
        self.mocked_extract(
            extract.patient_subrecord_csv,
            [[self.episode], Demographics, file_name]
        )
        headers = csv.writer().writerow.call_args_list[0][0][0]
        row = csv.writer().writerow.call_args_list[1][0][0]
        expected_headers = [
            'episode_id',
            'created',
            'updated',
            'created_by_id',
            'updated_by_id',
            'patient_id',
            'hospital_number',
            'nhs_number',
            'date_of_birth',
            'death_indicator',
            'sex',
            'birth_place',
        ]
        self.assertEqual(headers[0], 'episode_id')
        for h in expected_headers:
            self.assertTrue(h in headers)

        expected_row = [
            '1', u'None', u'None', u'None', u'None', '1', u'12345678',
            u'None', u'1976-01-01', u'False', u'', u''
        ]
        self.assertEqual(row, expected_row)


class ZipArchiveTestCase(PatientEpisodeTestCase):

    @patch('opal.core.search.extract.episode_subrecords')
    @patch('opal.core.search.extract.patient_subrecords')
    @patch('opal.core.search.extract.zipfile')
    def test_episode_subrecords(self, zipfile, patient_subrecords, episode_subrecords):
        episode_subrecords.return_value = [HatWearer]
        patient_subrecords.return_value = [HouseOwner]
        extract.zip_archive(models.Episode.objects.all(), 'this', self.user)
        self.assertEqual(4, zipfile.ZipFile.return_value.__enter__.return_value.write.call_count)

    @patch('opal.core.search.extract.episode_subrecord_csv')
    @patch('opal.core.search.extract.zipfile')
    def test_exclude_episode_subrecords(self, zipfile, subrecords):
        extract.zip_archive(models.Episode.objects.all(), 'this', self.user)
        subs = [a[0][1] for a in subrecords.call_args_list]
        self.assertFalse(Colour in subs)

    @patch('opal.core.search.extract.patient_subrecord_csv')
    @patch('opal.core.search.extract.zipfile')
    def test_exclude_patient_subrecords(self, zipfile, subrecords):
        extract.zip_archive(models.Episode.objects.all(), 'this', self.user)
        subs = [a[0][1] for a in subrecords.call_args_list]
        self.assertFalse(PatientColour in subs)


class AsyncExtractTestCase(OpalTestCase):

    @patch('opal.core.search.tasks.extract.delay')
    def test_async(self, delay):
        extract.async_extract(self.user, 'THIS')
        delay.assert_called_with(self.user, 'THIS')


class TestBasicCsvRenderer(OpalTestCase):
    def test_init(self):
        renderer = extract.CsvRenderer(Colour)
        self.assertEqual(renderer.model, Colour)
        renderer = extract.CsvRenderer(Colour)
        self.assertEqual(renderer.fields, renderer.get_field_names_to_render())

    def test_get_field_names_to_render(self):
        with patch.object(Colour, "_get_fieldnames_to_extract") as field_names:
            field_names.return_value = ["name", "consistency_token"]
            renderer = extract.CsvRenderer(Colour)
            self.assertEqual(
                renderer.fields,
                ["name"]
            )

    def test_get_headers(self):
        with patch.object(Colour, "_get_fieldnames_to_extract") as field_names:
            field_names.return_value = ["name", "consistency_token"]
            renderer = extract.CsvRenderer(Colour)
            self.assertEqual(
                renderer.get_headers(),
                ["name"]
            )

    def test_get_row(self):
        with patch.object(Colour, "_get_fieldnames_to_extract") as field_names:
            _, episode = self.new_patient_and_episode_please()
            colour = Colour.objects.create(name="Blue", episode=episode)
            field_names.return_value = ["name", "consistency_token"]
            renderer = extract.CsvRenderer(Colour)
            self.assertEqual(
                renderer.get_row(colour),
                ["Blue"]
            )


class TestEpisodeCsvRenderer(OpalTestCase):

    def test_init(self):
        renderer = extract.EpisodeCsvRenderer(self.user)
        self.assertEqual(renderer.model, models.Episode)

    def test_get_headers(self):
        renderer = extract.EpisodeCsvRenderer(self.user)
        _, episode = self.new_patient_and_episode_please()
        episode.set_tag_names(["trees", "leaves"], self.user)
        self.assertIn("tagging", renderer.get_headers())

    def test_get_row(self):
        renderer = extract.EpisodeCsvRenderer(self.user)
        _, episode = self.new_patient_and_episode_please()
        episode.set_tag_names(["trees", "leaves"], self.user)
        self.assertIn("trees;leaves", renderer.get_row(episode))



@patch.object(PatientColour, "_get_fieldnames_to_extract")
class TestPatientSubrecordCsvRenderer(OpalTestCase):

    def setUp(self):
        self.patient, self.episode = self.new_patient_and_episode_please()
        self.patient_colour = PatientColour.objects.create(
            name="blue", patient=self.patient
        )

    def test_get_header(self, field_names_to_extract):
        field_names_to_extract.return_value = [
            "patient_id", "name", "consistency_token", "id"
        ]
        renderer = extract.PatientSubrecordCsvRenderer(PatientColour)
        self.assertEqual(["episode_id", "patient_id", "name"], renderer.get_headers())

    def test_get_row(self, field_names_to_extract):
        field_names_to_extract.return_value = [
            "patient_id", "name", "consistency_token", "id"
        ]
        renderer = extract.PatientSubrecordCsvRenderer(PatientColour)
        rendered = renderer.get_row(self.patient_colour, self.episode.id)
        self.assertEqual(["1", "1", "blue"], rendered)


@patch.object(Colour, "_get_fieldnames_to_extract")
class TestEpisodeSubrecordCsvRenderer(OpalTestCase):

    def setUp(self):
        _, self.episode = self.new_patient_and_episode_please()
        self.colour = Colour.objects.create(
            name="blue", episode=self.episode
        )

    def test_get_header(self, field_names_to_extract):
        field_names_to_extract.return_value = [
            "episode_id", "name", "consistency_token", "id"
        ]
        renderer = extract.EpisodeSubrecordCsvRenderer(Colour)
        self.assertEqual(["patient_id", "episode_id", "name"], renderer.get_headers())

    def test_get_row(self, field_names_to_extract):
        field_names_to_extract.return_value = [
            "episode_id", "name", "consistency_token", "id"
        ]
        renderer = extract.EpisodeSubrecordCsvRenderer(Colour)
        rendered = renderer.get_row(self.colour)
        self.assertEqual(["1", "1", "blue"], rendered)



@patch.object(Colour, "_get_fieldnames_to_extract")
class TestInheritedRenderer(OpalTestCase):
    def setUp(self):
        class ColourCsvRenderer(extract.EpisodeSubrecordCsvRenderer):
            name = extract.Column(
                value=lambda self, instance: "Some value"
            )

        _, self.episode = self.new_patient_and_episode_please()
        self.colour = Colour.objects.create(
            name="blue", episode=self.episode
        )
        self.colourCsvRenderer = ColourCsvRenderer

    def test_get_header(self, field_names_to_extract):
        field_names_to_extract.return_value = [
            "episode_id", "name", "consistency_token", "id"
        ]
        renderer = self.colourCsvRenderer(Colour)
        expected = ['name', 'patient_id', 'episode_id']
        self.assertEqual(expected, renderer.get_headers())

    def test_get_rows(self, field_names_to_extract):
        field_names_to_extract.return_value = [
            "episode_id", "name", "consistency_token", "id"
        ]
        renderer = self.colourCsvRenderer(Colour)
        rendered = renderer.get_row(self.colour)
        self.assertEqual(["Some value", "1", "1"], rendered)
