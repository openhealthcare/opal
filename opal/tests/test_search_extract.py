"""
Unittests for opal.core.search.extract
"""
import datetime

from opal.core.test import OpalTestCase
from opal import models
from opal.tests.models import Colour, PatientColour, Demographics

from opal.core.search import extract

class SubrecordCSVTestCase(OpalTestCase):
    def setUp(self):
        self.patient = models.Patient.objects.create()
        self.episode = models.Episode.objects.create(patient=self.patient)
    
    def test_no_episodes(self):
        csv = extract.subrecord_csv([], Colour)
        self.assertIsInstance(csv, extract.ExtractCSV)
        self.assertEqual('colour.csv', csv.filename)
        self.assertEqual('episode_id,name', csv.contents)

    def test_with_subrecords(self):
        colour = Colour.objects.create(episode=self.episode, name='blue')
        
        csv = extract.subrecord_csv([self.episode], Colour)
        self.assertIsInstance(csv, extract.ExtractCSV)
        expected = 'episode_id,name\n{0},blue'.format(self.episode.id)
        self.assertEqual(expected, csv.contents)

    def test_with_subrecord_unicode(self):
        colour = Colour.objects.create(episode=self.episode, name=u'blueu\ua000')
        
        csv = extract.subrecord_csv([self.episode], Colour)
        self.assertIsInstance(csv, extract.ExtractCSV)
        expected = u'episode_id,name\n{0},blueu\ua000'.format(self.episode.id)
        self.assertEqual(expected, csv.contents)


class PatientSubrecordCSVTestCase(OpalTestCase):
    
    def setUp(self):
        self.patient = models.Patient.objects.create()
        self.episode = models.Episode.objects.create(patient=self.patient)

    def test_strips_pid(self):
        demographics = Demographics.objects.create(
            patient=self.patient,
            hospital_number='12345678',
            name='Alice Alderney',
            date_of_birth=datetime.date(1976,1,1)
        )
        csv = extract.patient_subrecord_csv([self.episode], Demographics)
        headers = csv.contents.split('\n')[0].split(',')

        self.assertIn('date_of_birth', headers)
        self.assertNotIn('name', headers)
