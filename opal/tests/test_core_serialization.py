"""
Unittests for opal.core.serialization
"""
import datetime
import six
import decimal
from django.test import override_settings
from django.utils import timezone

from opal.core import test

from opal.core import serialization


class DeserializeDatetimeTestCase(test.OpalTestCase):

    # runtests.py :
    DATETIME_INPUT_FORMATS=['%d/%m/%Y %H:%M:%S'],

    def test_deserialize_datetime(self):
        value = '22/04/1959 21:20:22'
        dt = serialization.deserialize_datetime(value)
        self.assertEqual(timezone.make_aware(datetime.datetime(1959, 4, 22, 21, 20, 22)), dt)

    def test_deserialize_invalid_datetime(self):
        with self.assertRaises(ValueError):
            value = '22-04-1959 21:20:22'
            dt = serialization.deserialize_datetime(value)

    def test_deserialize_already_a_datetime(self):
        value = timezone.make_aware(datetime.datetime(1959, 4, 22, 21, 20, 22))
        expected = timezone.make_aware(datetime.datetime(1959, 4, 22, 21, 20, 22))
        self.assertEqual(expected, serialization.deserialize_datetime(value))


class DeserializeTimeTestCase(test.OpalTestCase):
    # Django default:
    # TIME_INPUT_FORMATS
    # [
    #     '%H:%M:%S',     # '14:30:59'
    #     '%H:%M:%S.%f',  # '14:30:59.000200'
    #     '%H:%M',        # '14:30'
    # ]

    def test_deserialize_time(self):
        value = '14:30:59'
        t = serialization.deserialize_time(value)
        expected = timezone.make_aware(
            datetime.datetime(1, 1, 1, 14, 30, 59)
        ).time()
        self.assertEqual(expected, t)

    def test_deserialize_invalid_time(self):
        with self.assertRaises(ValueError):
            value = '14::30::59'
            serialization.deserialize_time(value)

    def test_deserialize_already_a_time(self):
        value = timezone.make_aware(
            datetime.datetime(1, 1, 1, 14, 30, 59)
        ).time()

        expected = timezone.make_aware(
            datetime.datetime(1, 1, 1, 14, 30, 59)
        ).time()
        self.assertEqual(expected, serialization.deserialize_time(value))


class DeserializeDateTestCase(test.OpalTestCase):

    # runtests.py :
    # DATE_INPUT_FORMATS=['%d/%m/%Y'],

    def test_deserialize_date(self):
        value = '22/04/1959'
        d = serialization.deserialize_date(value)
        self.assertEqual(datetime.date(1959, 4, 22), d)

    def test_deserialize_invalid_date(self):
        value = '22-04-1959'
        with self.assertRaises(ValueError):
            serialization.deserialize_date(value)

    def test_deserialize_already_a_date(self):
        value = datetime.date(1959, 4, 22)
        d = serialization.deserialize_date(value)
        self.assertEqual(datetime.date(1959, 4, 22), d)


class SerializerTestCase(test.OpalTestCase):

    def test_serializer_default_will_super(self):
        s = serialization.OpalSerializer()
        with self.assertRaises(TypeError):
            s.default(None)

    def test_binaries_become_utf_8(self):
        s = serialization.OpalSerializer()
        binary = six.b('Hello beautiful world. I am a binary.')
        serialized = s.default(binary)
        self.assertIsInstance(serialized, six.text_type)

    def test_serializer_time_serialisation(self):
        s = serialization.OpalSerializer()
        serialised = s.default(datetime.time(20))
        self.assertEqual(serialised, "20:00:00")

    def test_serialize_date_as_key(self):
        s = serialization.OpalSerializer()
        data = {
            datetime.date(1959, 3, 2): [
                "So What"
            ]
        }
        serialised = s.default(data)
        expected = {
            '02/03/1959': ['So What']
        }
        self.assertEqual(expected, serialised)

    def test_serialize_date_in_list(self):
        s = serialization.OpalSerializer()
        data = [datetime.date(1959, 4, 22), 11, 33]
        expected = ['22/04/1959', 11, 33]
        serialised = s.default(data)
        self.assertEqual(expected, serialised)

    def test_time_serialization(self):
        self.assertEqual(
            serialization.serialize_time(datetime.time(10, 30)),
            '10:30:00'
        )

    def test_date_serialization(self):
        self.assertEqual(
            serialization.serialize_date(datetime.date(2019, 4, 1)),
            '01/04/2019'
        )

    def test_datetime_serialization(self):
        self.assertEqual(
            serialization.serialize_datetime(
                datetime.datetime(2019, 4, 1, 10, 30)
            ),
            '01/04/2019 10:30:00'
        )

    def test_decimal_serialization(self):
        data = decimal.Decimal("12.00")
        serializer = serialization.OpalSerializer()
        serialised = serializer.default(data)
        self.assertEqual("12.00", serialised)
