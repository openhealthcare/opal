"""
Re-usable view components
"""
import functools
import json

from django.http import HttpResponse
from rest_framework import mixins, viewsets

from opal.core.serialization import OpalSerializer


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
