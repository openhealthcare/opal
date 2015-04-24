"""
OPAL Search views
"""
import datetime
import json

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic import View, TemplateView

from opal.core.views import LoginRequiredMixin, _build_json_response, _get_request_data
from opal.core.search.extract import zip_archive
from opal import models

class SaveFilterModalView(TemplateView):
    template_name = 'save_filter_modal.html'


class SearchTemplateView(TemplateView):
    template_name = 'search.html'


class ExtractTemplateView(TemplateView):
    template_name = 'extract.html'


class Extractor(View):

    def __init__(self, *a, **k):
        self.query = None
        return super(Extractor, self).__init__(*a, **k)

    def get_query(self):
        if not self.query:
            self.query = _get_request_data(self.request)
        return self.query

    def _episodes_for_boolean_fields(self, query, field, contains):
        model = query['column'].replace(' ', '_').lower()
        val = query['query'] == 'true'
        kw = {'{0}__{1}'.format(model.replace('_', ''), field): val}
        eps = models.Episode.objects.filter(**kw)
        return eps

    def _episodes_for_date_fields(self, query, field, contains):
        model = query['column'].replace(' ', '').lower()
        qtype = ''
        val = datetime.datetime.strptime(query['query'], "%d/%m/%Y")
        if query['queryType'] == 'Before':
            qtype = '__lte'
        elif query['queryType'] == 'After':
            qtype = '__gte'
        kw = {'{0}__{1}{2}'.format(model, field, qtype): val}
        eps = models.Episode.objects.filter(**kw)
        return eps

    def _episodes_for_fkorft_fields(self, query, field, contains, Mod):
        model = query['column'].replace(' ', '_').lower()

        # Look up to see if there is a synonym.
        content_type = ContentType.objects.get_for_model(getattr(Mod, field).foreign_model)
        name = query['query']
        try:
            from opal.models import Synonym
            synonym = Synonym.objects.get(content_type=content_type, name=name)
            name = synonym.content_object.name
        except Synonym.DoesNotExist: # maybe this is pointless exception bouncing?
            pass # That's fine.

        kw_fk = {'{0}__{1}_fk__name{2}'.format(model.replace('_', ''), field, contains): name}
        kw_ft = {'{0}__{1}_ft{2}'.format(model.replace('_', ''), field, contains): query['query']}

        if issubclass(Mod, models.EpisodeSubrecord):

            qs_fk = models.Episode.objects.filter(**kw_fk)
            qs_ft = models.Episode.objects.filter(**kw_ft)
            eps = set(list(qs_fk) + list(qs_ft))

        elif issubclass(Mod, models.PatientSubrecord):
            qs_fk = models.Patient.objects.filter(**kw_fk)
            qs_ft = models.Patient.objects.filter(**kw_ft)
            pats = set(list(qs_fk) + list(qs_ft))
            eps = []
            for p in pats:
                eps += list(p.episode_set.all())
        return eps

    def episodes_for_criteria(self, criteria):
        """
        Given one set of criteria, return episodes that match it.
        """
        from django.db import models as djangomodels

        query = criteria
        querytype = query['queryType']
        contains = '__iexact'
        if querytype == 'Contains':
            contains = '__icontains'

        model_name = query['column'].replace(' ', '').replace('_', '')
        field = query['field'].replace(' ', '_').lower()

        Mod = None
        for m in djangomodels.get_models():
            if m.__name__.lower() == model_name:
                if not Mod:
                    Mod = m
                elif (issubclass(m, models.EpisodeSubrecord) or
                      issubclass(m, models.PatientSubrecord)):
                    Mod = m

        if model_name.lower() == 'tags':
            Mod = models.Tagging

        named_fields = [f for f in Mod._meta.fields if f.name == field]

        if len(named_fields) == 1 and isinstance(named_fields[0],djangomodels.BooleanField):
            eps = self._episodes_for_boolean_fields(query, field, contains)

        elif len(named_fields) == 1 and isinstance(named_fields[0], djangomodels.DateField):
            eps = self._episodes_for_date_fields(query, field, contains)

        elif hasattr(Mod, field) and isinstance(getattr(Mod, field), fields.ForeignKeyOrFreeText):
            eps = self._episodes_for_fkorft_fields(query, field, contains, Mod)

        else:
            model = query['column'].replace(' ', '').lower()
            kw = {'{0}__{1}{2}'.format(model_name, field, contains): query['query']}

            if Mod == models.Tagging:
                eps = models.Episode.objects.ever_tagged(query['field'])

            elif issubclass(Mod, models.EpisodeSubrecord):
                eps = models.Episode.objects.filter(**kw)
            elif issubclass(Mod, models.PatientSubrecord):
                pats = models.Patient.objects.filter(**kw)
                eps = []
                for p in pats:
                    eps += list(p.episode_set.all())
        return eps

    def get_episodes(self):
        query = self.get_query()
        all_matches = [(q['combine'], self.episodes_for_criteria(q)) for q in query]
        if not all_matches:
            return []

        working = set(all_matches[0][1])
        rest = all_matches[1:]

        for combine, episodes in rest:
            methods = {'and': 'intersection', 'or': 'union', 'not': 'difference'}
            working = getattr(set(episodes), methods[combine])(working)

        eps = working
        return eps

    def episodes_as_json(self):
        eps = self.get_episodes()
        return [e.to_dict(self.request.user) for e in eps]

    def description(self):
        """
        Provide a textual description of the current search
        """
        query = self.get_query()
        filters = "\n".join("{combine} {column} {field} {queryType} {query}".format(**f) for f in query)
        return """{username} ({date})
Searching for:
{filters}
""".format(username=self.request.user.username, date=datetime.datetime.now(), filters=filters)


class ExtractSearchView(Extractor):
    def post(self, *args, **kwargs):
        eps = self.episodes_as_json()
        return _build_json_response(eps)


class DownloadSearchView(Extractor):
    def get_query(self):
        if not self.query:
            self.query = json.loads(self.request.POST['criteria'])
        return self.query

    def post(self, *args, **kwargs):
        fname = zip_archive(self.get_episodes(), self.description(), self.request.user)
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

