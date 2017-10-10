import datetime
from mock import mock_open, patch

from opal.core.test import OpalTestCase
from opal.tests.models import (
    PatientColour, Demographics, Colour, EpisodeName, FamousLastWords
)
from opal.core.search import extract_serialisers
from opal import models
from six import u, b  # NOQA


MOCKING_FILE_NAME_OPEN = "opal.core.search.extract_serialisers.open"


class TestEncodeToUTF8(OpalTestCase):
    def test_with_str(self):
        d = u('\u0160\u0110\u0106\u017d\u0107\u017e\u0161\u0111')
        r = b"\xc5\xa0\xc4\x90\xc4\x86\xc5\xbd\xc4\x87\xc5\xbe\xc5\xa1\xc4\x91"
        self.assertEqual(
            extract_serialisers._encode_to_utf8(d),
            r
        )

    def test_with_other(self):
        d = 2
        self.assertEqual(
            extract_serialisers._encode_to_utf8(d),
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
        renderer = extract_serialisers.PatientSubrecordCsvRenderer(
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
        renderer = extract_serialisers.PatientSubrecordCsvRenderer(
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
        renderer = extract_serialisers.PatientSubrecordCsvRenderer(
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

        renderer = extract_serialisers.PatientSubrecordCsvRenderer(
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


class TestBasicCsvRenderer(PatientEpisodeTestCase):
    def test_init(self):
        renderer = extract_serialisers.CsvRenderer(Colour, Colour.objects.all(), self.user)
        self.assertEqual(renderer.model, Colour)
        renderer = extract_serialisers.CsvRenderer(Colour, Colour.objects.all(), self.user)
        self.assertEqual(renderer.fields, renderer.get_field_names_to_render())

    def test_0_count(self):
        renderer = extract_serialisers.CsvRenderer(Colour, Colour.objects.all(), self.user)
        self.assertEqual(renderer.count(), 0)

    def test_1_count(self):
        Colour.objects.create(name="Blue", episode=self.episode)
        renderer = extract_serialisers.CsvRenderer(Colour, Colour.objects.all(), self.user)
        self.assertEqual(renderer.count(), 1)

    def test_set_fields(self):
        renderer = extract_serialisers.CsvRenderer(
            Colour, Colour.objects.all(), self.user, fields=[
                "name", "episode_id"
            ]
        )
        self.assertEqual(renderer.fields, ["name", "episode_id"])
        self.assertEqual(
            renderer.get_headers(),
            ["Name", "Episode"]
        )

    def test_get_field_names_to_render(self):
        with patch.object(Colour, "_get_fieldnames_to_extract") as field_names:
            field_names.return_value = ["name", "consistency_token"]
            renderer = extract_serialisers.CsvRenderer(
                Colour,  Colour.objects.all(), self.user
            )
            self.assertEqual(
                renderer.fields,
                ["name"]
            )

    def test_fields_uses_fields_arg(self):
            renderer = extract_serialisers.CsvRenderer(
                Colour,  Colour.objects.all(), self.user, fields=["name"]
            )
            self.assertEqual(
                renderer.fields,
                ["name"]
            )

    def test_get_headers(self):
        with patch.object(Colour, "_get_fieldnames_to_extract") as field_names:
            field_names.return_value = ["name", "consistency_token"]
            renderer = extract_serialisers.CsvRenderer(
                Colour, Colour.objects.all(), self.user
            )
            self.assertEqual(
                renderer.get_headers(),
                ["Name"]
            )

    def test_get_headers_uses_fields_arg(self):
            renderer = extract_serialisers.CsvRenderer(
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
            renderer = extract_serialisers.CsvRenderer(
                Colour, Colour.objects.all(), self.user
            )
            result = renderer.get_row(colour)
            self.assertIn(b"onions; kettles", result)

    def test_get_row(self):
        with patch.object(Colour, "_get_fieldnames_to_extract") as field_names:
            _, episode = self.new_patient_and_episode_please()
            colour = Colour.objects.create(name="Blue", episode=episode)
            field_names.return_value = ["name", "consistency_token"]
            renderer = extract_serialisers.CsvRenderer(
                Colour, Colour.objects.all(), self.user
            )
            self.assertEqual(
                renderer.get_row(colour),
                [b"Blue"]
            )

    def test_get_row_uses_fields_arg(self):
        _, episode = self.new_patient_and_episode_please()
        colour = Colour.objects.create(name="Blue", episode=episode)
        renderer = extract_serialisers.CsvRenderer(
            Colour,  Colour.objects.all(), self.user, fields=["name"]
        )
        self.assertEqual(
            renderer.get_row(colour),
            [b"Blue"]
        )

    def test_get_rows(self):
        _, episode = self.new_patient_and_episode_please()
        colour = Colour.objects.create(name="Blue", episode=episode)
        renderer = extract_serialisers.CsvRenderer(
            Colour, Colour.objects.all(), self.user
        )
        with patch.object(renderer, "get_row") as get_row:
            get_row.return_value = ["some_row"]
            result = list(renderer.get_rows())

        get_row.assert_called_with(colour)
        self.assertEqual(result, [["some_row"]])

    @patch("opal.core.search.extract_serialisers.csv")
    def test_write_to_file(self, csv):
        _, episode = self.new_patient_and_episode_please()
        Colour.objects.create(name="Blue", episode=episode)
        renderer = extract_serialisers.CsvRenderer(
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
                self.assertEqual(
                    csv.writer().writerow.mock_calls[0][1][0], ["header"]
                )
                self.assertEqual(
                    csv.writer().writerow.mock_calls[1][1][0], ["row"]
                )

    @patch('opal.core.search.extract_serialisers.schemas')
    def test_get_schema(self, schemas):
        schemas.extract_download_schema_for_model.return_value = "some_result"
        result = extract_serialisers.CsvRenderer.get_schema(FamousLastWords)
        schemas.extract_download_schema_for_model.assert_called_once_with(
            FamousLastWords
        )
        self.assertEqual(result, "some_result")


class TestEpisodeCsvRenderer(PatientEpisodeTestCase):

    def test_init(self):
        renderer = extract_serialisers.EpisodeCsvRenderer(
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
        renderer = extract_serialisers.EpisodeCsvRenderer(
            models.Episode,
            models.Episode.objects.all(),
            self.user
        )
        self.assertEqual(len(expected - set(renderer.get_headers())), 0)

    def test_get_row(self):
        renderer = extract_serialisers.EpisodeCsvRenderer(
            models.Episode,
            models.Episode.objects.all(),
            self.user
        )
        self.episode.set_tag_names(["trees"], self.user)
        # make sure we keep historic tags
        self.episode.set_tag_names(["leaves"], self.user)
        self.assertIn(b"trees;leaves", renderer.get_row(self.episode))

    def test_get_display_name(self):
        renderer = extract_serialisers.EpisodeCsvRenderer(
            models.Episode,
            models.Episode.objects.all(),
            self.user
        )

        self.assertEqual("Episode", renderer.get_display_name())

    @patch('opal.core.search.extract_serialisers.schemas')
    def test_get_schema(self, schemas):
        schemas.extract_download_schema_for_model.return_value = dict(
            fields=[]
        )
        self.assertEqual(
            extract_serialisers.EpisodeCsvRenderer.get_schema(models.Episode),
            dict(
                fields=[dict(
                    name="team",
                    title="Team",
                    type="string",
                    type_display_name="Text Field"
                )]
            )
        )
        schemas.extract_download_schema_for_model.assert_called_once_with(
            models.Episode
        )


class NestedEpisodeCsvRendererTestCase(PatientEpisodeTestCase):
    def setUp(self):
        super(NestedEpisodeCsvRendererTestCase, self).setUp()
        self.episode.start = datetime.date.today()
        self.renderer = extract_serialisers.EpisodeCsvRenderer(
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
        self.renderer = extract_serialisers.EpisodeSubrecordCsvRenderer(
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
        self.renderer = extract_serialisers.EpisodeSubrecordCsvRenderer(
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
        self.renderer = extract_serialisers.EpisodeSubrecordCsvRenderer(
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
        renderer = extract_serialisers.EpisodeSubrecordCsvRenderer(
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
        self.renderer = extract_serialisers.PatientSubrecordCsvRenderer(
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
        self.renderer = extract_serialisers.PatientSubrecordCsvRenderer(
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
        self.renderer = extract_serialisers.PatientSubrecordCsvRenderer(
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
        renderer = extract_serialisers.PatientSubrecordCsvRenderer(
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
        renderer = extract_serialisers.EpisodeSubrecordCsvRenderer(
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
        renderer = extract_serialisers.EpisodeSubrecordCsvRenderer(
            Colour, models.Episode.objects.all(), self.user
        )
        rendered = renderer.get_row(self.colour)
        self.assertEqual([b"1", b"1", b"blue"], rendered)


class TestExtractCsvSerialiser(PatientEpisodeTestCase):
    def test_get_model_for_episode_api_name(self):
        als = extract_serialisers.ExtractCsvSerialiser.get_model_for_api_name(
            "episode"
        )
        self.assertEqual(als, models.Episode)

    def test_get_model_for_subrecord_api_name(self):
        als = extract_serialisers.ExtractCsvSerialiser.get_model_for_api_name(
            "episode_name"
        )
        self.assertEqual(als, EpisodeName)

    @patch('opal.core.search.extract_serialisers.ExtractCsvSerialiser.list')
    @patch('opal.core.search.extract_serialisers.subrecords')
    def test_get_api_name_to_serialiser_cls_patient_subrecord(
        self, subrecords, discoverable_list
    ):
        discoverable_list.return_value = []
        subrecords.subrecords.return_value = [FamousLastWords]
        subrecords.patient_subrecords.return_value = [FamousLastWords]
        r = extract_serialisers.ExtractCsvSerialiser.api_name_to_serialiser_cls()
        ps = extract_serialisers.PatientSubrecordCsvRenderer
        self.assertEqual(
            r, dict(
                famous_last_words=ps
            )
        )

    @patch('opal.core.search.extract_serialisers.ExtractCsvSerialiser.list')
    @patch('opal.core.search.extract_serialisers.subrecords')
    def test_get_api_name_to_serialiser_cls_episode_subrecord(
        self, subrecords, discoverable_list
    ):
        discoverable_list.return_value = []
        subrecords.subrecords.return_value = [EpisodeName]
        subrecords.patient_subrecords.return_value = []
        r = extract_serialisers.ExtractCsvSerialiser.api_name_to_serialiser_cls()
        es = extract_serialisers.EpisodeSubrecordCsvRenderer
        self.assertEqual(
            r, dict(
                episode_name=es
            )
        )

    @patch('opal.core.search.extract_serialisers.ExtractCsvSerialiser.list')
    @patch('opal.core.search.extract_serialisers.subrecords')
    def test_get_api_name_to_serialiser_cls_excluded(
        self, subrecords, discoverable_list
    ):
        discoverable_list.return_value = []
        subrecords.subrecords.return_value = [PatientColour]
        subrecords.patient_subrecords.return_value = [PatientColour]
        r = extract_serialisers.ExtractCsvSerialiser.api_name_to_serialiser_cls()
        self.assertEqual(
            r, dict()
        )

    @patch('opal.core.search.extract_serialisers.ExtractCsvSerialiser.list')
    @patch('opal.core.search.extract_serialisers.subrecords')
    def test_get_api_name_to_serialiser_cls_overridden(
        self, subrecords, discoverable_list
    ):
        class EpisodeNameOverride(
            extract_serialisers.ExtractCsvSerialiser
        ):
            slug = "episode_name"
        discoverable_list.return_value = [EpisodeNameOverride]
        subrecords.subrecords.return_value = [EpisodeName]
        r = extract_serialisers.ExtractCsvSerialiser.api_name_to_serialiser_cls()
        self.assertEqual(
            r, dict(episode_name=EpisodeNameOverride)
        )

    @patch('opal.core.search.extract_serialisers.subrecords')
    @patch(
        'opal.core.search.extract_serialisers.EpisodeCsvRenderer.get_schema'
    )
    @patch('opal.core.search.extract_serialisers.CsvRenderer.get_schema')
    def test_get_data_dictionary_schema(
        self, get_schema, episode_get_schema, subrecords
    ):
        episode_get_schema.return_value = dict(display_name="episode schema")
        get_schema.return_value = dict(display_name="csv schema")
        subrecords.subrecords.return_value = (EpisodeName, PatientColour,)
        ecs = extract_serialisers.ExtractCsvSerialiser
        result = ecs.get_data_dictionary_schema()
        self.assertEqual(
            result, [get_schema.return_value, episode_get_schema.return_value]
        )
        episode_get_schema.assert_called_once_with(models.Episode)
        # we don't call patient colour because its excluded
        get_schema.assert_called_once_with(EpisodeName)
