"""
Unittests for opal.management.commands.create_random_data
"""
import datetime
from unittest.mock import patch, MagicMock

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

    def test_date_generator_same_day(self):
        start = datetime.date.today()
        end = datetime.date.today()
        date = crd.date_generator(start_date=start, end_date=end)
        self.assertEqual(date.today(), date)

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

    def test_get_birth_date_returns_date(self):
        self.assertIsInstance(self.gen.get_birth_date(), datetime.date)

    def test_create_episode(self):
        patient = Patient.objects.create()
        self.assertEqual(0, patient.episode_set.count())
        with patch.object(crd.random, 'choice') as randchoice:
            randchoice.return_value = True
            self.gen.create_episode(patient)
            randchoice.assert_called_with([True, False])
        self.assertEqual(1, patient.episode_set.count())

    def test_make(self):
        self.assertEqual(0, Patient.objects.count())
        p = self.gen.make()
        self.assertEqual(1, Patient.objects.count())


class SubrecordGeneratorTestCase(OpalTestCase):

    def test_is_null_field_for_null_boolean(self):
        generator = crd.SubRecordGenerator()
        with patch.object(crd.random, 'randint') as randint:
            randint.return_value = 1

            self.assertEqual(True, generator.is_null_field(crd.NullBooleanField))

    def test_is_empty_string(self):
        generator = crd.SubRecordGenerator()
        with patch.object(crd.random, 'randint') as randint:
            randint.return_value = 1

            self.assertEqual(True, generator.is_empty_string_field(
                crd.CharField
            ))

    def test_make_empty_string_fields(self):
        p, e = self.new_patient_and_episode_please()
        with patch.object(crd.EpisodeSubrecordGenerator, 'get_instance') as get_instance:
            generator = crd.EpisodeSubrecordGenerator(crd.models.Demographics, e)
            with patch.object(crd.SubRecordGenerator, 'is_null_field') as null_field:
                null_field.return_value = False
                with patch.object(generator, 'is_empty_string_field') as empty_string:
                    empty_string.return_value = True
                    mock_instance = MagicMock(name='Mock Instance')
                    get_instance.return_value = mock_instance
                    generator.make()
                    self.assertEqual("", mock_instance.post_code)


class CommandTestCase(OpalTestCase):

    def test_add_arguments(self):
        c = crd.Command()
        parser = MagicMock()
        c.add_arguments(parser)
        parser.add_argument.assert_called_once_with(
            '--number',
            dest='number',
            help="how many would you like to create",
            default=100
        )

    def test_handle(self):
        com = crd.Command()
        with patch.object(crd.PatientGenerator, 'make') as maker:
            com.handle(number='23')
            self.assertEqual(23, maker.call_count)

    def test_handle_default_100(self):
        com = crd.Command()
        with patch.object(crd.PatientGenerator, 'make') as maker:
            com.handle(number=None)
            self.assertEqual(100, maker.call_count)
