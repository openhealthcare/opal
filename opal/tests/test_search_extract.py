"""
Unittests for opal.core.search.extract
"""
import datetime
from mock import mock_open, Mock, patch


from opal.core.test import OpalTestCase
from opal import models
from opal.tests.models import Colour, PatientColour, Demographics

from opal.core.search import extract

MOCKING_FILE_NAME_OPEN = "opal.core.search.extract.open"


class PatientEpisodeTestCase(OpalTestCase):
    def setUp(self):
        self.patient = models.Patient.objects.create()
        self.episode = models.Episode.objects.create(patient=self.patient)
        Demographics.objects.all().update(
            patient=self.patient,
            hospital_number='12345678',
            name='Alice Alderney',
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
            extract.subrecord_csv,
            [[], Colour, file_name]
        )
        headers = csv.writer().writerow.call_args_list[0][0][0]
        self.assertEqual(csv.writer().writerow.call_count, 1)
        self.assertEqual(headers, ['episode_id', 'name'])

    @patch("opal.core.search.extract.csv")
    def test_with_subrecords(self, csv):
        csv.writer = Mock()
        file_name = "fake file name"
        colour = Colour.objects.create(episode=self.episode, name='blue')

        self.mocked_extract(
            extract.subrecord_csv,
            [[self.episode], Colour, file_name]
        )

        headers = csv.writer().writerow.call_args_list[0][0][0]
        row = csv.writer().writerow.call_args_list[1][0][0]
        expected_headers = ['episode_id', 'name']
        expected_row = [self.episode.id, 'blue']
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
            'episode_id', 'hospital_number', 'date_of_birth', u'gender_fk_id', 'gender_ft', 'gender'
        ]

        expected_row = [
            1, u'12345678', datetime.date(1976, 1, 1), None, u'', u''
        ]
        self.assertEqual(headers, expected_headers)
        self.assertEqual(row, expected_row)
