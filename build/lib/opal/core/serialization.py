"""
Opal [de]seralization helpers
"""
import datetime

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from django.utils.dateformat import format
import six


def deserialize_datetime(value):
    """
    Given a VALUE, deserialize it to a datetime
    """
    if isinstance(value, datetime.datetime):
        return value

    input_format = settings.DATETIME_INPUT_FORMATS[0]
    value = timezone.make_aware(datetime.datetime.strptime(
        value, input_format
    ), timezone.get_current_timezone())

    return value


def deserialize_time(value):
    """
    Given a VALUE, deserialize it to a time
    """
    if isinstance(value, datetime.time):
        return value

    input_format = settings.TIME_INPUT_FORMATS[0]
    value = timezone.make_aware(datetime.datetime.strptime(
        value, input_format
    ), timezone.get_current_timezone()).time()

    return value


def deserialize_date(value):
    """
    Given a VALUE, deserialize it to a date
    """
    if isinstance(value, datetime.date):
        return value

    input_format = settings.DATE_INPUT_FORMATS[0]
    dt = datetime.datetime.strptime(
        value, input_format
    )
    dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt.date()


class OpalSerializer(DjangoJSONEncoder):
    """
    Render a dict as JSON
    """
    def default(self, o):
        if isinstance(o, six.binary_type):
            return o.decode('utf-8')
        if isinstance(o, datetime.time):
            return format(o, settings.TIME_FORMAT)
        elif isinstance(o, datetime.datetime):
            return format(o, settings.DATETIME_FORMAT)
        elif isinstance(o, datetime.date):
            return format(
                datetime.datetime.combine(
                    o, datetime.datetime.min.time()
                ), settings.DATE_FORMAT
            )
        super(OpalSerializer, self).default(o)
