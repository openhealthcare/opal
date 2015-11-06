"""
OPAL Search views
"""
import datetime
import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.http import require_http_methods
from django.views.generic import View, TemplateView
from django.core.paginator import Paginator

from opal import models
from opal.core.views import (LoginRequiredMixin, _build_json_response,
                             _get_request_data, with_no_caching)
from opal.core.search import queries
from opal.core.search.extract import zip_archive, async_extract

PAGINATION_AMOUNT = 10


class SaveFilterModalView(TemplateView):
    template_name = 'save_filter_modal.html'


class SearchTemplateView(TemplateView):
    template_name = 'search.html'


class ExtractTemplateView(TemplateView):
    template_name = 'extract.html'


def _add_pagination(eps, page_number):
    paginator = Paginator(eps, PAGINATION_AMOUNT)
    results = {
        "object_list": paginator.page(page_number).object_list,
        "page_number": page_number,
        "total_pages": paginator.num_pages,
        "total_count": len(eps),
    }
    return results


def _extract_basic_search_parameters(request):
    ''' fills in the basic search criteria if we want
    to search via a hospital number or name
    '''
    criteria = {
        u'column': u'demographics',
        u'combine': u'or',
        u'queryType': u'Contains'
    }

    hospital_number = request.GET.get("hospital_number")
    name = request.GET.get("name")
    result = []

    if hospital_number is not None:
        query_criteria = criteria.copy()
        query_criteria['field'] = 'Hospital Number'
        query_criteria['query'] = hospital_number
        result.append(query_criteria)

    if name is not None:
        query_criteria = criteria.copy()
        query_criteria['field'] = 'name'
        query_criteria['query'] = name
        result.append(query_criteria)

    return result


@with_no_caching
@require_http_methods(['GET'])
def patient_search_view(request):
    hospital_number = request.GET.get("hospital_number")

    if hospital_number is None:
        return _build_json_response({'error': "No search terms"}, 400)

    criteria = [{
        "queryType": "Equals",
        "query": hospital_number,
        "field": "Hospital Number",
        'combine': 'and',
        'column': u'demographics',
    }]

    query = queries.SearchBackend(request.user, criteria)
    return _build_json_response(query.patients_as_json())


@with_no_caching
@require_http_methods(['GET'])
def simple_search_view(request):
    page_number = int(request.GET.get("page_number", 1))
    all_criteria = _extract_basic_search_parameters(request)

    if not all_criteria:
        return _build_json_response({'error': "No search terms"}, 400)

    query = queries.SearchBackend(request.user, all_criteria)
    eps = query.get_patient_summaries()
    return _build_json_response(_add_pagination(eps, page_number))


class ExtractSearchView(View):
    def post(self, *args, **kwargs):
        request_data = _get_request_data(self.request)
        page_number = 1

        if "page_number" in request_data[0]:
            page_number = request_data[0].pop("page_number", 1)

        query = queries.SearchBackend(
            self.request.user,
            request_data,
        )
        eps = query.get_patient_summaries()

        return _build_json_response(_add_pagination(eps, page_number))


class DownloadSearchView(View):

    def post(self, *args, **kwargs):
        if getattr(settings, 'EXTRACT_ASYNC', None):
            criteria = _get_request_data(self.request)['criteria']
            extract_id = async_extract(
                self.request.user,
                json.loads(criteria)
            )
            return _build_json_response({'extract_id': extract_id})

        query = queries.SearchBackend(
            self.request.user, json.loads(self.request.POST['criteria'])
        )
        episodes = query.get_episodes()
        fname = zip_archive(episodes, query.description(), self.request.user)
        resp = HttpResponse(open(fname, 'rb').read())
        disp = 'attachment; filename="{0}extract{1}.zip"'.format(
            settings.OPAL_BRAND_NAME, datetime.datetime.now().isoformat())
        resp['Content-Disposition'] = disp
        return resp


class FilterView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        filters = models.Filter.objects.filter(user=self.request.user)
        return _build_json_response([f.to_dict() for f in filters])

    def post(self, *args, **kwargs):
        data = _get_request_data(self.request)
        self.filter = models.Filter(user=self.request.user)
        self.filter.update_from_dict(data)
        return _build_json_response(self.filter.to_dict())


class FilterDetailView(LoginRequiredMixin, View):
    def dispatch(self, *args, **kwargs):
        try:
            self.filter = models.Filter.objects.get(pk=kwargs['pk'])
        except models.Episode.DoesNotExist:
            return HttpResponseNotFound()
        return super(FilterDetailView, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        return _build_json_response(self.filter)

    def put(self, *args, **kwargs):
        data = _get_request_data(self.request)
        self.filter.update_from_dict(data)
        return _build_json_response(self.filter.to_dict())

    def delete(self, *args, **kwargs):
        self.filter.delete()
        return _build_json_response('')


class ExtractResultView(View):
                
    def get(self, *args, **kwargs):
        """
        Tell the client about the state of the extract
        """
        from celery.result import AsyncResult
        import taskrunner
        task_id = kwargs['task_id']
        result = AsyncResult(id=task_id, app=taskrunner.celery.app)
        print result.state 
        
        return _build_json_response({'state': result.state})
                

class ExtractFileView(View):
    def get(self, *args, **kwargs):
        from celery.result import AsyncResult
        import taskrunner
        task_id = kwargs['task_id']
        result = AsyncResult(id=task_id, app=taskrunner.celery.app)
        if result.state != 'SUCCESS':
            raise ValueError('Wrong Task Larry!')
        print result.state
        fname = result.get() 
        resp = HttpResponse(open(fname, 'rb').read())
        disp = 'attachment; filename="{0}extract{1}.zip"'.format(
            settings.OPAL_BRAND_NAME, datetime.datetime.now().isoformat())
        resp['Content-Disposition'] = disp
        return resp        
