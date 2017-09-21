"""
Unittests for opal.core.search.extract
"""
import datetime
from collections import OrderedDict

from mock import mock_open, patch

from opal.core.test import OpalTestCase
from opal import models
from opal.tests.models import (
    Colour, PatientColour, Demographics, HatWearer, HouseOwner, EpisodeName,
    FamousLastWords
)
from opal.core.search import extract
from six import u, b


MOCKING_FILE_NAME_OPEN = "opal.core.search.extract.open"


class TestEncodeToUTF8(OpalTestCase):
    def test_with_str(self):
        d = u('\u0160\u0110\u0106\u017d\u0107\u017e\u0161\u0111')
        r = b"\xc5\xa0\xc4\x90\xc4\x86\xc5\xbd\xc4\x87\xc5\xbe\xc5\xa1\xc4\x91"
        self.assertEqual(
            extract._encode_to_utf8(d),
            r
        )

    def test_with_other(self):
        d = 2
        self.assertEqual(
            extract._encode_to_utf8(d),
            d
        )


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


class GenerateMultiFilesTestCase(OpalTestCase):
    @patch('opal.core.search.extract.subrecords.subrecords')
    @patch('opal.core.search.extract.CsvRenderer.write_to_file')
    @patch('opal.core.search.extract.write_data_dictionary')
    def test_generate_multi_csv_extract(
        self, write_data_dictionary, write_to_file, subrecords
    ):
        patient, episode = self.new_patient_and_episode_please()
        subrecords.return_value = [HatWearer, HouseOwner]
        HatWearer.objects.create(name="Indiana", episode=episode)
        HouseOwner.objects.create(patient=patient)
        results = extract.generate_multi_csv_extract(
            "somewhere", models.Episode.objects.all(), self.user
        )
        expected = [
            ('somewhere/data_dictionary.html', 'data_dictionary.html'),
            ('somewhere/episodes.csv', 'episodes.csv'),
            ('somewhere/hat_wearer.csv', 'hat_wearer.csv'),
            ('somewhere/house_owner.csv', 'house_owner.csv')
        ]
        self.assertEqual(expected, results)
        self.assertEqual(
            write_data_dictionary.call_args[0][0],
            'somewhere/data_dictionary.html'
        )
        self.assertEqual(
            write_to_file.call_args[0], ('somewhere/house_owner.csv',)
        )

    @patch('opal.core.search.extract.subrecords.subrecords')
    @patch('opal.core.search.extract.EpisodeSubrecordCsvRenderer')
    @patch('opal.core.search.extract.CsvRenderer.write_to_file')
    @patch('opal.core.search.extract.write_data_dictionary')
    def test_exclude_subrecords(
        self, write_data_dictionary, write_to_file, csv_renderer, subrecords
    ):
        subrecords.return_value = [Colour]
        extract.generate_multi_csv_extract(
            "somewhere", models.Episode.objects.all(), self.user
        )
        self.assertEqual(csv_renderer.call_count, 0)


@patch('opal.core.search.extract.csv')
@patch('opal.core.search.extract.write_data_dictionary')
class GenerateNestedFilesTestCase(OpalTestCase):
    def test_with_non_asci_charecters(
        self, write_data_dictionary, csv
    ):
        patient, episode = self.new_patient_and_episode_please()
        HatWearer.objects.create(
            name=u("\u0160\u0110\u0106\u017d\u0107\u017e\u0161\u0111"),
            wearing_a_hat=False,
            episode=episode
        )
        field_args = {}
        field_args[HatWearer.get_api_name()] = [
            'name'
        ]
        m = mock_open()
        with patch(MOCKING_FILE_NAME_OPEN, m, create=True):
            extract.generate_nested_csv_extract(
                "somewhere",
                models.Episode.objects.all(),
                self.user,
                field_args
            )

        r = b"\xc5\xa0\xc4\x90\xc4\x86\xc5\xbd\xc4\x87\xc5\xbe\xc5\xa1\xc4\x91"
        self.assertEqual(
            csv.writer().writerow.call_args_list[0][0][0][0],
            'Wearer of Hats Name'
        )
        self.assertEqual(
            csv.writer().writerow.call_args_list[1][0][0][0],
            r
        )

    def test_generate_nested_csv_extract(
        self, write_data_dictionary, csv
    ):
        patient, episode = self.new_patient_and_episode_please()
        HatWearer.objects.create(name="Indiana", episode=episode)
        HatWearer.objects.create(
            name="Tommy Cooper",
            wearing_a_hat=False,
            episode=episode
        )
        FamousLastWords.objects.update(
            words="oops",
            patient=patient
        )
        m = mock_open()
        field_args = OrderedDict()
        field_args[FamousLastWords.get_api_name()] = [
            'words'
        ]
        field_args[HatWearer.get_api_name()] = [
            'name',
            'wearing_a_hat'
        ]

        with patch(MOCKING_FILE_NAME_OPEN, m, create=True):
            results = extract.generate_nested_csv_extract(
                "somewhere",
                models.Episode.objects.all(),
                self.user,
                field_args
            )
        expected = [
            ('somewhere/data_dictionary.html', 'data_dictionary.html'),
            ('somewhere/extract.csv', 'extract.csv'),
        ]
        self.assertEqual(expected, results)
        self.assertEqual(
            write_data_dictionary.call_args[0][0],
            'somewhere/data_dictionary.html'
        )

        write_row = csv.writer().writerow;

        self.assertEqual(
            len(write_row.call_args_list[0][0][0]),
            len(write_row.call_args_list[1][0][0]),
        )

        expected_headers = [
            'Famous Last Words Only Words',
            'Wearer of Hats 1 Name',
            'Wearer of Hats 1 Wearing A Hat',
            'Wearer of Hats 2 Name',
            'Wearer of Hats 2 Wearing A Hat'
        ]
        self.assertEqual(
            write_row.call_args_list[0][0][0],
            expected_headers
        )

        expected_row = [
            b'oops',
            b'Indiana',
            b'True',
            b'Tommy Cooper',
            b'False'
        ]

        self.assertEqual(
            write_row.call_args_list[1][0][0],
            expected_row
        )

    def test_generate_nested_csv_extract_with_episode(
        self, write_data_dictionary, csv
    ):
        patient, episode = self.new_patient_and_episode_please()
        episode.start = datetime.date(2017, 1, 12)
        episode.save()
        HatWearer.objects.create(name="Indiana", episode=episode)
        HatWearer.objects.create(
            name="Tommy Cooper",
            wearing_a_hat=False,
            episode=episode
        )
        FamousLastWords.objects.update(
            words="oops",
            patient=patient
        )
        m = mock_open()
        field_args = OrderedDict()
        field_args["episode"] = [
            'start'
        ]
        field_args[HatWearer.get_api_name()] = [
            'name',
            'wearing_a_hat'
        ]

        with patch(MOCKING_FILE_NAME_OPEN, m, create=True):
            results = extract.generate_nested_csv_extract(
                "somewhere",
                models.Episode.objects.all(),
                self.user,
                field_args
            )
        expected = [
            ('somewhere/data_dictionary.html', 'data_dictionary.html'),
            ('somewhere/extract.csv', 'extract.csv'),
        ]
        self.assertEqual(expected, results)
        self.assertEqual(
            write_data_dictionary.call_args[0][0],
            'somewhere/data_dictionary.html'
        )

        write_row = csv.writer().writerow;

        self.assertEqual(
            len(write_row.call_args_list[0][0][0]),
            len(write_row.call_args_list[1][0][0]),
        )

        expected_headers = [
            'Episode Start',
            'Wearer of Hats 1 Name',
            'Wearer of Hats 1 Wearing A Hat',
            'Wearer of Hats 2 Name',
            'Wearer of Hats 2 Wearing A Hat'
        ]
        self.assertEqual(
            write_row.call_args_list[0][0][0],
            expected_headers
        )

        expected_row = [
            datetime.date(2017, 1, 12),
            b'Indiana',
            b'True',
            b'Tommy Cooper',
            b'False'
        ]

        self.assertEqual(
            write_row.call_args_list[1][0][0],
            expected_row
        )


@patch('opal.core.search.extract.subrecords.subrecords')
@patch('opal.core.search.extract.zipfile')
class ZipArchiveTestCase(OpalTestCase):
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

    def test_subrecords_if_empty_query(self, zipfile, subrecords):
        # if there are no subrecords we don't expect them to write to the file
        subrecords.return_value = [HatWearer, HouseOwner]
        extract.zip_archive(models.Episode.objects.all(), 'this', self.user)
        call_args = zipfile.ZipFile.return_value.__enter__.return_value.write.call_args_list
        self.assertEqual(2, len(call_args))
        self.assertTrue(call_args[0][0][0].endswith("data_dictionary.html"))
        self.assertTrue(call_args[1][0][0].endswith("episodes.csv"))

    @patch('opal.core.search.extract.generate_nested_csv_extract')
    @patch('opal.core.search.extract.generate_multi_csv_extract')
    def test_nested_extract_called(self, multi, nested, zipfile, subrecords):
        extract.zip_archive(
            models.Episode.objects.all(),
            'this',
            self.user,
            fields="some fields"
        )
        self.assertTrue(nested.call_count, 1)
        self.assertFalse(multi.called)

    @patch('opal.core.search.extract.generate_nested_csv_extract')
    @patch('opal.core.search.extract.generate_multi_csv_extract')
    def test_nested_extract_not_called(
        self, multi, nested, zipfile, subrecords
    ):
        extract.zip_archive(
            models.Episode.objects.all(),
            'this',
            self.user,
        )
        self.assertTrue(multi.call_count, 1)
        self.assertFalse(nested.called)


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
            self.assertIn(b"onions; kettles", result)

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
                [b"Blue"]
            )

    def test_get_row_uses_fields_arg(self):
        _, episode = self.new_patient_and_episode_please()
        colour = Colour.objects.create(name="Blue", episode=episode)
        renderer = extract.CsvRenderer(
            Colour,  Colour.objects.all(), self.user, fields=["name"]
        )
        self.assertEqual(
            renderer.get_row(colour),
            [b"Blue"]
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
            "Team"
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
        self.assertIn(b"trees;leaves", renderer.get_row(self.episode))


@patch.object(PatientColour, "_get_fieldnames_to_extract")
class TestPatientSubrecordCsvRenderer(PatientEpisodeTestCase):

    def setUp(self):
        self.patient, self.episode = self.new_patient_and_episode_please()
        self.patient_colour = PatientColour.objects.create(
            name="blue", patient=self.patient
        )

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
        self.assertEqual([b"1", b"1", b"blue"], rendered)

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
        self.assertEqual([[b"1", b"1", b"blue"]], rendered)

    def test_get_rows_same_patient(self, field_names_to_extract):
        self.patient.create_episode()
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
            [b"1", b"1", b"blue"],
            [b"2", b"1", b"blue"]
        ], rendered)


class NestedEpisodeCsvRendererTestCase(PatientEpisodeTestCase):
    def setUp(self):
        super(NestedEpisodeCsvRendererTestCase, self).setUp()
        self.episode.start = datetime.date.today()
        self.renderer = extract.EpisodeCsvRenderer(
            models.Episode,
            models.Episode.objects.all(),
            self.user,
            fields=["start"]
        )

    def test_get_headers(self):
        self.assertEqual(
            self.renderer.get_flat_headers(),
            ["Episode Start"]
        )

    def test_nested_get_row(self):
        self.assertEqual(
            self.renderer.get_nested_row(self.episode),
            [datetime.date.today()]
        )


class NestedEpisodeSubrecordCsvRendererTestCase(PatientEpisodeTestCase):
    def setUp(self):
        super(NestedEpisodeSubrecordCsvRendererTestCase, self).setUp()
        self.patient_2, self.episode_2 = self.new_patient_and_episode_please()
        self.colour_1 = Colour.objects.create(
            name="blue", episode=self.episode
        )
        self.colour_2 = Colour.objects.create(
            name="green", episode=self.episode
        )
        self.renderer = extract.EpisodeSubrecordCsvRenderer(
            Colour,
            models.Episode.objects.all(),
            self.user,
            fields=["name"]
        )

    def test_repetitions(self):
        self.assertEqual(self.renderer.flat_repetitions, 2)

    def test_row_length(self):
        self.assertEqual(self.renderer.flat_row_length, 2)

    def test_get_headers(self):
        self.assertEqual(
            self.renderer.get_flat_headers(),
            ["Colour 1 Name", "Colour 2 Name"]
        )

    def test_get_nested_row_populated(self):
        result = self.renderer.get_nested_row(self.episode)
        self.assertEqual(
            result, [b'blue', b'green']
        )

    def test_get_nested_row_not_populated(self):
        result = self.renderer.get_nested_row(
            self.episode_2
        )
        self.assertEqual(
            result, ['', '']
        )


class NestedEpisodeSubrecordCsvRendererWhenNoneTestCase(
    PatientEpisodeTestCase
):
    def setUp(self):
        super(NestedEpisodeSubrecordCsvRendererWhenNoneTestCase, self).setUp()
        self.colour = Colour.objects.create(
            name="blue", episode=self.episode
        )
        self.renderer = extract.EpisodeSubrecordCsvRenderer(
            Colour,
            models.Episode.objects.all(),
            self.user,
            fields=["name"]
        )

    def test_repetitions(self):
        self.assertEqual(self.renderer.flat_repetitions, 1)

    def test_row_length(self):
        self.assertEqual(self.renderer.flat_row_length, 1)

    def test_get_headers(self):
        self.assertEqual(
            self.renderer.get_flat_headers(),
            ['Colour Name']
        )

    def test_get_nested_row_populated(self):
        result = self.renderer.get_nested_row(self.episode)
        self.assertEqual(
            result, [b'blue']
        )


class NestedEpisodeSubrecordCsvRendererWhenOneTestCase(
    PatientEpisodeTestCase
):
    def setUp(self):
        super(NestedEpisodeSubrecordCsvRendererWhenOneTestCase, self).setUp()
        self.renderer = extract.EpisodeSubrecordCsvRenderer(
            Colour,
            models.Episode.objects.all(),
            self.user,
            fields=["name"]
        )

    def test_repetitions(self):
        self.assertEqual(self.renderer.flat_repetitions, 0)

    def test_row_length(self):
        self.assertEqual(self.renderer.flat_row_length, 0)

    def test_get_headers(self):
        self.assertEqual(
            self.renderer.get_flat_headers(),
            []
        )

    def test_get_nested_row_populated(self):
        result = self.renderer.get_nested_row(self.episode)
        self.assertEqual(
            result, []
        )

    def test_with_singleton(self):
        renderer = extract.EpisodeSubrecordCsvRenderer(
            EpisodeName,
            models.Episode.objects.all(),
            self.user,
            fields=["name"]
        )
        self.assertEqual(renderer.flat_repetitions, 1)


class NestedPatientSubrecordCsvRendererTestCase(PatientEpisodeTestCase):
    def setUp(self):
        super(NestedPatientSubrecordCsvRendererTestCase, self).setUp()
        self.patient_2, self.episode_2 = self.new_patient_and_episode_please()
        self.colour_1 = PatientColour.objects.create(
            name="blue", patient=self.patient
        )
        self.colour_2 = PatientColour.objects.create(
            name="green", patient=self.patient
        )
        self.renderer = extract.PatientSubrecordCsvRenderer(
            PatientColour,
            models.Episode.objects.all(),
            self.user,
            fields=["name"]
        )

    def test_repetitions(self):
        self.assertEqual(self.renderer.flat_repetitions, 2)

    def test_row_length(self):
        self.assertEqual(self.renderer.flat_row_length, 2)

    def test_get_headers(self):
        self.assertEqual(
            self.renderer.get_flat_headers(),
            ["Patient Colour 1 Name", "Patient Colour 2 Name"]
        )

    def test_get_nested_row_populated(self):
        result = self.renderer.get_nested_row(self.episode)
        self.assertEqual(
            result, [b'blue', b'green']
        )

    def test_get_nested_row_not_populated(self):
        result = self.renderer.get_nested_row(self.episode_2)
        self.assertEqual(
            result, ['', '']
        )


class NestedPatientSubrecordCsvRendererWhenNoneTestCase(
    PatientEpisodeTestCase
):
    def setUp(self):
        super(NestedPatientSubrecordCsvRendererWhenNoneTestCase, self).setUp()
        self.colour = PatientColour.objects.create(
            name="blue", patient=self.patient
        )
        self.renderer = extract.PatientSubrecordCsvRenderer(
            PatientColour,
            models.Episode.objects.all(),
            self.user,
            fields=["name"]
        )

    def test_repetitions(self):
        self.assertEqual(self.renderer.flat_repetitions, 1)

    def test_row_length(self):
        self.assertEqual(self.renderer.flat_row_length, 1)

    def test_get_headers(self):
        self.assertEqual(
            self.renderer.get_flat_headers(),
            ['Patient Colour Name']
        )

    def test_get_nested_row_populated(self):
        result = self.renderer.get_nested_row(self.episode)
        self.assertEqual(
            result, [b'blue']
        )


class NestedPatientSubrecordCsvRendererWhenOneTestCase(
    PatientEpisodeTestCase
):
    def setUp(self):
        super(NestedPatientSubrecordCsvRendererWhenOneTestCase, self).setUp()
        self.renderer = extract.PatientSubrecordCsvRenderer(
            PatientColour,
            models.Episode.objects.all(),
            self.user,
            fields=["name"]
        )

    def test_repetitions(self):
        self.assertEqual(self.renderer.flat_repetitions, 0)

    def test_row_length(self):
        self.assertEqual(self.renderer.flat_row_length, 0)

    def test_get_headers(self):
        self.assertEqual(
            self.renderer.get_flat_headers(),
            []
        )

    def test_get_nested_row_populated(self):
        result = self.renderer.get_nested_row(self.episode)
        self.assertEqual(
            result, []
        )

    def test_with_singleton(self):
        renderer = extract.PatientSubrecordCsvRenderer(
            FamousLastWords,
            models.Episode.objects.all(),
            self.user,
            fields=["name"]
        )
        self.assertEqual(renderer.flat_repetitions, 1)


@patch.object(Colour, "_get_fieldnames_to_extract")
class TestEpisodeSubrecordCsvRenderer(PatientEpisodeTestCase):
    def setUp(self):
        _, self.episode = self.new_patient_and_episode_please()
        self.colour = Colour.objects.create(
            name="blue", episode=self.episode
        )

    def test_get_header(self, field_names_to_extract):
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
        field_names_to_extract.return_value = [
            "episode_id", "name", "consistency_token", "id"
        ]
        renderer = extract.EpisodeSubrecordCsvRenderer(
            Colour, models.Episode.objects.all(), self.user
        )
        rendered = renderer.get_row(self.colour)
        self.assertEqual([b"1", b"1", b"blue"], rendered)
