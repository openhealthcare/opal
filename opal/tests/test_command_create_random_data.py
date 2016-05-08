"""
Unittests for opal.management.commands.create_random_data
"""
import datetime
from mock import patch, MagicMock

from opal.core.test import OpalTestCase
from opal.models import Patient

from opal.management.commands import create_random_data as crd

class StringGeneratorTestCase(OpalTestCase):
    def test_string_generator(self):
        mock_field = MagicMock(name='Mock Field')
        mock_field.max_length = 30
        frist, last = crd.string_generator(mock_field).split()
        self.assertIn(frist, crd.adjectives)
        self.assertIn(last, crd.nouns)


class ConsistencyGeneratorTestCase(OpalTestCase):
    def test_consistency_generator(self):
        res = crd.consistency_generator()
        self.assertIsInstance(res, str)
        self.assertEqual(8, len(res))


class DateGeneratorTestCase(OpalTestCase):

    def test_date_generator_returns_date(self):
        self.assertIsInstance(crd.date_generator(), datetime.date)

    def test_date_generator_partial_year(self):
        start = datetime.date(2016, 3, 1)
        end = datetime.date(2016, 5, 1)
        date = crd.date_generator(start_date=start, end_date=end)
        self.assertIsInstance(date, datetime.date)
        self.assertGreaterEqual(date, start)
        self.assertLessEqual(date, end)

    def test_date_generator_single_month(self):
        start = datetime.date(2016, 3, 1)
        end = datetime.date(2016, 3, 15)
        date = crd.date_generator(start_date=start, end_date=end)
        self.assertIsInstance(date, datetime.date)
        self.assertGreaterEqual(date, start)
        self.assertLessEqual(date, end)

class DateTimeGeneratorTestCase(OpalTestCase):
    def test_datetime_generator_returns_datetime(self):
        self.assertIsInstance(crd.date_time_generator(), datetime.datetime)

    @patch('opal.management.commands.create_random_data.date')
    def test_datetime_generator_on_leap_day(self, date):
        date.today.return_value = datetime.date(2016, 2, 29)
        date.side_effect = lambda *args, **kw: datetime.date(*args, **kw)
        self.assertIsInstance(crd.date_time_generator(), datetime.datetime)


class ForeignKeyOrFreeTextGenerator(OpalTestCase):
    def test_no_options(self):
        mock_field = MagicMock(name='MockField')
        vlist = mock_field.foreign_model.objects.all.return_value.values_list
        vlist.return_value = []
        with patch.object(crd.random, 'randint') as randint:
            randint.return_value = 9
            result = crd.foreign_key_or_free_text_generator(mock_field)
            self.assertEqual(None, result)

    def test_has_options(self):
        mock_field = MagicMock(name='MockField')
        vlist = mock_field.foreign_model.objects.all.return_value.values_list
        vlist.return_value = ['the option']
        with patch.object(crd.random, 'randint') as randint:
            randint.return_value = 9
            result = crd.foreign_key_or_free_text_generator(mock_field)
            self.assertEqual('the option', result)

    def test_free_text(self):
        mock_field = MagicMock(name='MockField')
        vlist = mock_field.foreign_model.objects.all.return_value.values_list
        vlist.return_value = ['the option']
        with patch.object(crd.random, 'randint') as randint:
            randint.return_value = 1
            with patch.object(crd, 'string_generator') as stringgen:
                stringgen.return_value = 'the string'
                result = crd.foreign_key_or_free_text_generator(mock_field)
                stringgen.assert_called_with(mock_field)
                self.assertEqual('the string', result)


class TextFieldGeneratorTestCase(OpalTestCase):
    def test_text_field_generator(self):
        result = crd.text_field_generator()
        self.assertIsInstance(result, str)


class BooleanFieldGeneratorTestCase(OpalTestCase):
    def test_boolean(self):
        self.assertIn(crd.boolean_field_generator(), [True, False])


class PatientGeneratorTestCase(OpalTestCase):
    def setUp(self):
        self.gen = crd.PatientGenerator()

    def test_get_name(self):
        name = self.gen.get_name()
        frist, last = name.split()
        self.assertIsInstance(name, str)
        self.assertIn(frist, crd.first_names)
        self.assertIn(last, crd.last_names)

    def test_get_birth_date_returns_date(self):
        self.assertIsInstance(self.gen.get_birth_date(), datetime.date)

    def test_get_unique_hospital_numbers(self):
        numbers = self.gen.get_unique_hospital_numbers(10)
        self.assertEqual(10, len(numbers))

    def test_create_episode(self):
        patient = Patient.objects.create()
        self.assertEqual(0, patient.episode_set.count())
        with patch.object(crd.random, 'choice') as randchoice:
            randchoice.return_value = True
            episode = self.gen.create_episode(patient)
            randchoice.assert_called_with([True, False])
        self.assertEqual(1, patient.episode_set.count())

    def test_make(self):
        self.assertEqual(0, Patient.objects.count())
        p = self.gen.make()
        self.assertEqual(1, Patient.objects.count())
