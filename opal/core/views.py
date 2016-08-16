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
from rest_framework import mixins, viewsets
from django.conf import settings


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class OpalSerializer(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
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
    return json.loads(data)

def _build_json_response(data, status_code=200):
    response = HttpResponse()
    response['Content-Type'] = 'application/json'
    response.content = json.dumps(data, cls=OpalSerializer)
    # response.content = '<html><body>'+json.dumps(data, cls=DjangoJSONEncoder)+'</body></html>'
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
