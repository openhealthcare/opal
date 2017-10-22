"""
Unittests for opal.core.search.extract
"""
import datetime
from collections import OrderedDict

from mock import mock_open, patch
import os.path

from opal.core.test import OpalTestCase
from opal import models
from opal.tests.models import (
    PatientColour, Demographics, HatWearer, HouseOwner, FamousLastWords
)
from opal.core.search import extract, extract_serialisers
from six import u, b  # NOQA


MOCKING_FILE_NAME_OPEN = "opal.core.search.extract.open"


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
    @patch(
        'opal.core.search.extract.ExtractCsvSerialiser.\
api_name_to_serialiser_cls'
    )
    @patch('opal.core.search.extract.write_data_dictionary')
    def test_generate_multi_csv_extract(
        self, write_data_dictionary, api_name_to_serialiser_cls
    ):
        patient, episode = self.new_patient_and_episode_please()
        api_name_to_serialiser_cls.return_value = {
            "hat_wearer": extract_serialisers.EpisodeSubrecordCsvRenderer,
            "house_owner": extract_serialisers.PatientSubrecordCsvRenderer,
            "episode": extract_serialisers.EpisodeCsvRenderer
        }

        HatWearer.objects.create(name="Indiana", episode=episode)
        HouseOwner.objects.create(patient=patient)
        with patch.object(
            extract_serialisers.PatientSubrecordCsvRenderer,
            "write_to_file"
        ) as ps_write_to_file:
            with patch.object(
                extract_serialisers.EpisodeSubrecordCsvRenderer,
                "write_to_file"
            ) as es_write_to_file:
                with patch.object(
                    extract_serialisers.EpisodeCsvRenderer,
                    "write_to_file"
                ) as e_write_to_file:
                    results = set(extract.generate_multi_csv_extract(
                        "somewhere", models.Episode.objects.all(), self.user
                    ))

        ps_write_to_file.assert_called_once_with('somewhere/house_owner.csv')
        es_write_to_file.assert_called_once_with('somewhere/hat_wearer.csv')
        e_write_to_file.assert_called_once_with('somewhere/episode.csv')
        expected = set([
            ('somewhere/data_dictionary.html', 'data_dictionary.html'),
            ('somewhere/hat_wearer.csv', 'hat_wearer.csv'),
            ('somewhere/house_owner.csv', 'house_owner.csv'),
            ('somewhere/episode.csv', 'episode.csv')
        ])
        self.assertEqual(expected, results)
        self.assertEqual(
            write_data_dictionary.call_args[0][0],
            'somewhere/data_dictionary.html'
        )


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

        write_row = csv.writer().writerow

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

    def test_generate_nested_csv_extract_with_excluded(
        self, write_data_dictionary, csv
    ):
        """ Patient Colour is excluded from advanced search
            so we shouldn't be able to pull it out
        """
        patient, episode = self.new_patient_and_episode_please()
        episode.start = datetime.date(2017, 1, 12)
        episode.save()
        PatientColour.objects.create(name="Blue", patient=patient)
        field_args = {}
        field_args[PatientColour.get_api_name()] = [
            'name',
        ]
        field_args["episode"] = [
            'start',
        ]

        m = mock_open()
        with patch(MOCKING_FILE_NAME_OPEN, m, create=True):
            extract.generate_nested_csv_extract(
                "somewhere",
                models.Episode.objects.all(),
                self.user,
                field_args
            )
        self.assertEqual(
            csv.writer().writerow.call_args_list[0][0][0][0],
            "Episode Start"
        )
        self.assertEqual(
            csv.writer().writerow.call_args_list[1][0][0][0],
            datetime.date(2017, 1, 12)
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

        write_row = csv.writer().writerow

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


class WriteDescriptionTestCase(OpalTestCase):
    def test_with_fields(self):
        m = mock_open()
        with patch(MOCKING_FILE_NAME_OPEN, m, create=True):
            extract.write_description(
                models.Episode.objects.all(),
                self.user,
                "some_description",
                "some_dir",
                fields=dict(demographics=["birth_place", "death_indicator"])
            )
        m().write.assert_called_once_with(
            "some_description \nExtracting:\nDemographics - Birth Place, \
Death Indicator"
        )

    def test_with_fields_and_muiltiple_subrecords(self):
        m = mock_open()
        with patch(MOCKING_FILE_NAME_OPEN, m, create=True):
            extract.write_description(
                models.Episode.objects.all(),
                self.user,
                "some_description",
                "some_dir",
                fields=dict(
                    demographics=["birth_place", "death_indicator"],
                    location=["ward"]
                )
            )
        m().write.assert_called_once_with(
            'some_description \nExtracting:\nDemographics - Birth Place, Death Indicator\nLocation - Ward'
        )

    def test_with_multiple_where_one_is_not_advanced_searchable(self):
        """ testing description for multiple subrecords where
            one is not advanced searchable
        """
        m = mock_open()
        with patch(MOCKING_FILE_NAME_OPEN, m, create=True):
            extract.write_description(
                models.Episode.objects.all(),
                self.user,
                "some_description",
                "some_dir",
                fields=dict(
                    demographics=["birth_place", "death_indicator"],
                    patient_colour=["name"]
                )
            )
        m().write.assert_called_once_with(
            "some_description \nExtracting:\nDemographics - Birth Place, \
Death Indicator"
        )

    def test_with_multiple_where_is_not_advanced_searchable(self):
        m = mock_open()
        with patch(MOCKING_FILE_NAME_OPEN, m, create=True):
            extract.write_description(
                models.Episode.objects.all(),
                self.user,
                "some_description",
                "some_dir",
                fields=dict(
                    patient_colour=["name"]
                )
            )
        m().write.assert_called_once_with(
            "some_description"
        )

    def test_with_out_fields(self):
        m = mock_open()
        with patch(MOCKING_FILE_NAME_OPEN, m, create=True):
            extract.write_description(
                models.Episode.objects.all(),
                self.user,
                "some_description",
                "some_dir",
            )
        m().write.assert_called_once_with(
            "some_description"
        )


@patch('opal.core.search.extract.ExtractCsvSerialiser.\
api_name_to_serialiser_cls'
)
@patch('opal.core.search.extract.zipfile')
class ZipArchiveTestCase(OpalTestCase):
    def test_subrecords(self, zipfile, api_name_to_serialiser_cls):
        patient, episode = self.new_patient_and_episode_please()
        api_name_to_serialiser_cls.return_value = {
            "hat_wearer": extract_serialisers.EpisodeSubrecordCsvRenderer,
            "house_owner": extract_serialisers.PatientSubrecordCsvRenderer,
            "episode": extract_serialisers.EpisodeCsvRenderer
        }

        HatWearer.objects.create(name="Indiana", episode=episode)
        HouseOwner.objects.create(patient=patient)
        extract.zip_archive(models.Episode.objects.all(), 'this', self.user)
        call_args = zipfile.ZipFile.return_value.__enter__.return_value.write.call_args_list
        self.assertEqual(5, len(call_args))
        base_names = {os.path.basename(i[0][0]) for i in call_args}
        expected = {
            "query.txt",
            "data_dictionary.html",
            "hat_wearer.csv",
            "house_owner.csv",
            "episode.csv"
        }
        self.assertEqual(base_names, expected)

    def test_subrecords_if_none(self, zipfile, api_name_to_serialiser_cls):
        # if there are no subrecords we don't expect them to write to the file
        patient, episode = self.new_patient_and_episode_please()
        api_name_to_serialiser_cls.return_value = {
            "hat_wearer": extract_serialisers.EpisodeSubrecordCsvRenderer,
            "house_owner": extract_serialisers.PatientSubrecordCsvRenderer,
            "episode": extract_serialisers.EpisodeCsvRenderer
        }
        HouseOwner.objects.create(patient=patient)
        extract.zip_archive(models.Episode.objects.all(), 'this', self.user)
        call_args = zipfile.ZipFile.return_value.__enter__.return_value.write.call_args_list
        self.assertEqual(4, len(call_args))
        base_names = {os.path.basename(i[0][0]) for i in call_args}
        expected = {
            "query.txt",
            "data_dictionary.html",
            "house_owner.csv",
            "episode.csv"
        }
        self.assertEqual(base_names, expected)

    def test_subrecords_if_empty_query(self, zipfile, api_name_to_serialiser_cls):
        # if there are no subrecords we don't expect them to write to the file
        api_name_to_serialiser_cls.return_value = {
            "hat_wearer": extract_serialisers.EpisodeSubrecordCsvRenderer,
            "house_owner": extract_serialisers.PatientSubrecordCsvRenderer,
            "episode": extract_serialisers.EpisodeCsvRenderer
        }
        extract.zip_archive(models.Episode.objects.all(), 'this', self.user)
        call_args = zipfile.ZipFile.return_value.__enter__.return_value.write.call_args_list
        self.assertEqual(3, len(call_args))
        self.assertTrue(call_args[0][0][0].endswith("query.txt"))
        self.assertTrue(call_args[1][0][0].endswith("data_dictionary.html"))
        self.assertTrue(call_args[2][0][0].endswith("episode.csv"))

    @patch('opal.core.search.extract.os')
    @patch('opal.core.search.extract.write_description')
    @patch('opal.core.search.extract.generate_nested_csv_extract')
    @patch('opal.core.search.extract.generate_multi_csv_extract')
    def test_nested_extract_called(
        self,
        multi,
        nested,
        write_description,
        os,
        zipfile,
        api_name_to_serialiser_cls
    ):
        write_description.return_value = ("some_file_path", "some_file",)
        os.path.join.return_value = "some_temp_dir"
        fields = dict(episode=["start"])
        all_episodes = models.Episode.objects.all()
        extract.zip_archive(
            all_episodes,
            'this',
            self.user,
            fields=fields
        )
        self.assertTrue(nested.call_count, 1)
        self.assertFalse(multi.called)
        write_description.assert_called_once_with(
            all_episodes,
            self.user,
            "this",
            "some_temp_dir",
            fields=fields
        )

    @patch('opal.core.search.extract.os')
    @patch('opal.core.search.extract.write_description')
    @patch('opal.core.search.extract.generate_nested_csv_extract')
    @patch('opal.core.search.extract.generate_multi_csv_extract')
    def test_nested_extract_not_called(
        self,
        multi,
        nested,
        write_description,
        os,
        zipfile,
        api_name_to_serialiser_cls
    ):
        write_description.return_value = ("some_file_path", "some_file",)
        os.path.join.return_value = "some_temp_dir"
        all_episodes = models.Episode.objects.all()
        extract.zip_archive(
            all_episodes,
            'this',
            self.user,
        )
        self.assertTrue(multi.call_count, 1)
        self.assertFalse(nested.called)
        write_description.assert_called_once_with(
            all_episodes,
            self.user,
            "this",
            "some_temp_dir",
            fields=None
        )


class AsyncExtractTestCase(OpalTestCase):

    @patch('opal.core.search.tasks.extract.delay')
    def test_async(self, delay):
        extract.async_extract(self.user, 'THIS')
        delay.assert_called_with(self.user, 'THIS')
