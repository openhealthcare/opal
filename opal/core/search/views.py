"""
Opal Search views
"""
import datetime
import json
from functools import wraps

from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.http import require_http_methods
from django.views.generic import View, TemplateView
from django.core.paginator import Paginator

from rest_framework import status

from opal import models
from opal.core.views import (LoginRequiredMixin, json_response,
                             _get_request_data, with_no_caching)
from opal.core.search import queries
from opal.core.search.extract import zip_archive, async_extract

PAGINATION_AMOUNT = 10


class SaveFilterModalView(TemplateView):
    template_name = 'save_filter_modal.html'


class SearchTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'search.html'


class ExtractTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'extract.html'


def ajax_login_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated():
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


def ajax_login_required_view(view):
    @wraps(view)
    def wrapper(self, *args, **kwargs):
        if not self.request.user.is_authenticated():
            raise PermissionDenied
        return view(self, *args, **kwargs)
    return wrapper


def _add_pagination(eps, page_number):
    paginator = Paginator(eps, PAGINATION_AMOUNT)
    results = {
        "object_list": paginator.page(page_number).object_list,
        "page_number": page_number,
        "total_pages": paginator.num_pages,
        "total_count": len(eps),
    }
    return results


@with_no_caching
@require_http_methods(['GET'])
@ajax_login_required
def patient_search_view(request):
    hospital_number = request.GET.get("hospital_number")

    if hospital_number is None:
        return json_response({'error': "No search terms"}, 400)

    criteria = [{
        "queryType": "Equals",
        "query": hospital_number,
        "field": "Hospital Number",
        'combine': 'and',
        'column': u'demographics',
    }]

    query = queries.create_query(request.user, criteria)
    return json_response(query.patients_as_json())


@with_no_caching
@require_http_methods(['GET'])
@ajax_login_required
def simple_search_view(request):
    page_number = int(request.GET.get("page_number", 1))
    query_string = request.GET.get("query")
    if not query_string:
        return json_response({'error': "No search terms"}, 400)

    query = queries.create_query(request.user, query_string)
    result = query.fuzzy_query()
    return json_response(_add_pagination(result, page_number))


class ExtractSearchView(View):
    @ajax_login_required_view
    def post(self, *args, **kwargs):
        request_data = _get_request_data(self.request)
        page_number = 1

        if not request_data:
            return json_response(
                dict(error="No search criteria provied"),
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if "page_number" in request_data[0]:
            page_number = request_data[0].pop("page_number", 1)

        query = queries.create_query(
            self.request.user,
            request_data,
        )
        eps = query.get_patient_summaries()

        return json_response(_add_pagination(eps, page_number))


class DownloadSearchView(View):
    @ajax_login_required_view
    def post(self, *args, **kwargs):
        if getattr(settings, 'EXTRACT_ASYNC', None):
            criteria = _get_request_data(self.request)['criteria']
            extract_id = async_extract(
                self.request.user,
                json.loads(criteria)
            )
            return json_response({'extract_id': extract_id})

        query = queries.create_query(
            self.request.user, json.loads(self.request.POST['criteria'])
        )
        episodes = query.get_episodes()
        fname = zip_archive(episodes, query.description(), self.request.user)
        resp = HttpResponse(open(fname, 'rb').read())
        disp = 'attachment; filename="{0}extract{1}.zip"'.format(
            settings.OPAL_BRAND_NAME, datetime.datetime.now().isoformat())
        resp['Content-Disposition'] = disp
        return resp


class FilterView(View):

    @ajax_login_required_view
    def dispatch(self, *args, **kwargs):
        return super(FilterView, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        filters = models.Filter.objects.filter(user=self.request.user)
        return json_response([f.to_dict() for f in filters])

    def post(self, *args, **kwargs):
        data = _get_request_data(self.request)
        self.filter = models.Filter(user=self.request.user)
        self.filter.update_from_dict(data)
        return json_response(self.filter.to_dict())


class FilterDetailView(View):
    @ajax_login_required_view
    def dispatch(self, *args, **kwargs):
        try:
            self.filter = models.Filter.objects.get(pk=kwargs['pk'])
        except models.Filter.DoesNotExist:
            return HttpResponseNotFound()
        return super(FilterDetailView, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        return json_response(self.filter.to_dict())

    def put(self, *args, **kwargs):
        data = _get_request_data(self.request)
        self.filter.update_from_dict(data)
        return json_response(self.filter.to_dict())

    def delete(self, *args, **kwargs):
        self.filter.delete()
        return json_response('')


class ExtractResultView(View):
    @ajax_login_required_view
    def get(self, *args, **kwargs):
        """
        Tell the client about the state of the extract
        """
        from celery.result import AsyncResult
        from opal.core import celery
        task_id = kwargs['task_id']
        result = AsyncResult(id=task_id, app=celery.app)

        return json_response({'state': result.state})


class ExtractFileView(View):

    @ajax_login_required_view
    def get(self, *args, **kwargs):
        from celery.result import AsyncResult
        from opal.core import celery
        task_id = kwargs['task_id']
        result = AsyncResult(id=task_id, app=celery.app)
        if result.state != 'SUCCESS':
            raise ValueError('Wrong Task Larry!')
        fname = result.get()
        with open(fname, 'rb') as fh:
            contents = fh.read()
        resp = HttpResponse(contents)
        disp = 'attachment; filename="{0}extract{1}.zip"'.format(
            settings.OPAL_BRAND_NAME, datetime.datetime.now().isoformat())
        resp['Content-Disposition'] = disp
        return resp
