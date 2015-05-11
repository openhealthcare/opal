"""
OPAL Search views
"""
import datetime
import json

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic import View, TemplateView

from opal import models
#from opal.core import fields
from opal.core.views import LoginRequiredMixin, _build_json_response, _get_request_data
from opal.core.search import queries
from opal.core.search.extract import zip_archive

class SaveFilterModalView(TemplateView):
    template_name = 'save_filter_modal.html'


class SearchTemplateView(TemplateView):
    template_name = 'search.html'


class ExtractTemplateView(TemplateView):
    template_name = 'extract.html'


class ExtractSearchView(View):
    def post(self, *args, **kwargs):
        query = queries.SearchBackend(self.request.user, _get_request_data(self.request))
        eps = query.episodes_as_json()
        return _build_json_response(eps)


class DownloadSearchView(View):

    def post(self, *args, **kwargs):
        query = queies.SearchBackend(self.request.user, json.loads(self.request.POST['criteria']))
        episodes = query.get_episodes()
        fname = zip_archive(episodes, query.description(), self.request.user)
        resp = HttpResponse(
            open(fname, 'rb').read(),
            mimetype='application/force-download'
            )
        resp['Content-Disposition'] = 'attachment; filename="{0}extract{1}.zip"'.format(
            settings.OPAL_BRAND_NAME, datetime.datetime.now().isoformat())
        return resp


class FilterView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        filters = models.Filter.objects.filter(user=self.request.user);
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

