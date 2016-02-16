"""
Unittests for opal.management.commands.create_random_data
"""
import datetime
from mock import patch, MagicMock

from opal.core.test import OpalTestCase

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


class DateTimeGeneratorTestCase(OpalTestCase):
    def test_datetime_generator_returns_datetime(self):
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
