"""
Re-usable view components
"""
import functools
import json
import datetime

from django.utils.dateformat import format
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from rest_framework import mixins, viewsets
import six


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class OpalSerializer(DjangoJSONEncoder):
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


def _get_request_data(request):
    data = request.read()
    if hasattr(data, 'decode'):
        data = data.decode('UTF-8')
    return json.loads(data)


def json_response(data, status_code=200):
    """
    Return a HTTPResponse serializing DATA with the correct serializer
    """
    response = HttpResponse()
    response['Content-Type'] = 'application/json'
    response.data = data
    response.content = json.dumps(data, cls=OpalSerializer)
    response.status_code = status_code
    return response


def with_no_caching(view):
    @functools.wraps(view)
    def no_cache(*args, **kw):
        response = view(*args, **kw)
        response['Cache-Control'] = 'no-cache'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '-1'
        return response

    return no_cache


class ModelViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    pass
