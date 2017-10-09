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
from six import u, b  # NOQA


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
            date_of_birth=datetime.date(1976, 1, 1),
            sex_ft=u('\u0160\u0110\u0106\u017d\u0107\u017e\u0161\u0111'),
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
            extract.subrecord_csv,
            [[], Colour, file_name]
        )
        headers = csv.writer().writerow.call_args_list[0][0][0]
        self.assertEqual(csv.writer().writerow.call_count, 1)
        expected_headers = [
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
        Colour.objects.create(episode=self.episode, name='blue')

        self.mocked_extract(
            extract.subrecord_csv,
            [[self.episode], Colour, file_name]
        )

        headers = csv.writer().writerow.call_args_list[0][0][0]
        row = csv.writer().writerow.call_args_list[1][0][0]
        expected_headers = [
            'created',
            'updated',
            'created_by_id',
            'updated_by_id',
            'episode_id',
            'name',
        ]
        expected_row = [
            None, None, None, None, self.episode.id, b'blue'
        ]
        self.assertEqual(headers, expected_headers)
        self.assertEqual(row, expected_row)


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
            1,
            None,
            None,
            None,
            None,
            b'12345678',
            None,
            datetime.date(1976, 1, 1),
            False,
            '\xc5\xa0\xc4\x90\xc4\x86\xc5\xbd\xc4\x87\xc5\xbe\xc5\xa1\xc4\x91',
            ''
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

    @patch('opal.core.search.extract.subrecord_csv')
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
