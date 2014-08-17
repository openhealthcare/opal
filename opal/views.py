"""
OPAL Viewz!
"""
import collections
import datetime
import json

from django.contrib.auth.views import login
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic import TemplateView, View
from django.views.decorators.http import require_http_methods
from django.template.loader import select_template
from django.utils.decorators import method_decorator
from django.utils import formats
from django.shortcuts import redirect
from django.template.loader import select_template

from opal.utils.http import with_no_caching
from opal.utils import (camelcase_to_underscore, stringport, fields, 
                        json_to_csv, OpalPlugin)
from opal.utils.banned_passwords import banned
from opal.utils.models import LookupList
from opal.utils.views import LoginRequiredMixin
from opal import models, exceptions

schema = stringport(settings.OPAL_SCHEMA_MODULE)
options = stringport(settings.OPAL_OPTIONS_MODULE)
flow = stringport(settings.OPAL_FLOW_MODULE)
micro_test_defaults = options.micro_test_defaults
option_models = models.option_models
Synonym = models.Synonym

LIST_SCHEMAS = {}
for plugin in OpalPlugin.__subclasses__():
    LIST_SCHEMAS.update(plugin().list_schemas())
LIST_SCHEMAS.update(schema.list_schemas.copy())

def _get_request_data(request):
    data = request.read()
    return json.loads(data)

def _build_json_response(data, status_code=200):
    response = HttpResponse()
    response['Content-Type'] = 'application/json'
    response.content = json.dumps(data, cls=DjangoJSONEncoder)
    # response.content = '<html><body>'+json.dumps(data, cls=DjangoJSONEncoder)+'</body></html>'
    response.status_code = status_code
    return response

def serve_maybe(meth):
    """
    Decorator to figure out if we want to serve files
    ourselves (DEBUG) or hand off to Nginx
    """
    def handoff(self, *args, **kwargs):
        """
        Internal wrapper function to figure out
        the logic
        """
        filename = meth(self, *args, **kwargs)

        # When we're running locally, just take the hit, otherwise
        # offload the serving of the datafile to Nginx
        if settings.DEBUG:
            resp = HttpResponse(
                open(filename, 'rb').read(),
                mimetype='application/force-download'
                )
            return resp

        resp = HttpResponse()
        url = '/protected/{0}'.format(filename)
        # let nginx determine the correct content type
        resp['Content-Type']=""
        resp['X-Accel-Redirect'] = url
        return resp

    return handoff


@require_http_methods(['GET', 'PUT'])
def episode_detail_view(request, pk):
    try:
        episode = models.Episode.objects.get(pk=pk)
    except models.Episode.DoesNotExist:
        return HttpResponseNotFound()

    if request.method == 'GET':
        serialized = episode.to_dict(request.user)
        return _build_json_response(serialized)

    data = _get_request_data(request)

    try:
        episode.update_from_dict(data, request.user)
        return _build_json_response(episode.to_dict(request.user, shallow=True))
    except exceptions.ConsistencyError:
        return _build_json_response({'error': 'Item has changed'}, 409)


@with_no_caching
@require_http_methods(['GET'])
def patient_search_view(request):
    GET = request.GET

    search_terms = {}
    filter_dict = {}

    if 'hospital_number' in GET:
        search_terms['hospital_number'] = GET['hospital_number']
        filter_dict['demographics__hospital_number__iexact'] = GET['hospital_number']

    if 'name' in GET:
        search_terms['name'] = GET['name']
        filter_dict['demographics__name__icontains'] = GET['name']

    if filter_dict:
        # TODO maybe limit/paginate results?
        # TODO maybe only return demographics & location
        patients = models.Patient.objects.filter(
            **filter_dict).order_by('demographics__date_of_birth')

        return _build_json_response([patient.to_dict(request.user)
                                     for patient in patients])
    else:
        return _build_json_response({'error': 'No search terms'}, 400)


@require_http_methods(['GET', 'POST'])
def episode_list_and_create_view(request):
    if request.method == 'GET':
        GET = request.GET
        if 'discharged' in GET:
            today = datetime.date.today()
            one_week_ago = today - datetime.timedelta(days=7)

            episodes = models.Episode.objects.filter(discharge_date__gte=one_week_ago)
            episode_ids = [e.id for e in episodes]
            historic = models.Tagging.historic_tags_for_episodes(episode_ids)
            serialised = [episode.to_dict(request.user)
                          for episode in episodes]
            for episode in serialised:
                if episode['id'] in historic:
                    historic_tags = historic[episode['id']]
                    for t in historic_tags.keys():
                        episode['tagging'][0][t] = True

        else:
            serialised = models.Episode.objects.serialised_active(request.user)
        return _build_json_response(serialised)

    elif request.method == 'POST':
        data = _get_request_data(request)
        hospital_number = data['demographics'].get('hospital_number')
        if hospital_number:
            patient, _ = models.Patient.objects.get_or_create(
                demographics__hospital_number=hospital_number)
        else:
            patient = models.Patient.objects.create()

        patient.update_from_demographics_dict(data['demographics'], request.user)
        try:
            episode = patient.create_episode()
            episode_fields = models.Episode._get_fieldnames_to_serialize()
            episode_data = {}
            for fname in episode_fields:
                if fname in data:
                    episode_data[fname] = data[fname]
            episode.update_from_dict(episode_data, request.user)

        except exceptions.APIError:
            return _build_json_response(
                {'error': 'Patient already has active episode'}, 400)

        episode.update_from_location_dict(data['location'], request.user)
        if 'tagging' in data:
            tag_names = [n for n, v in data['tagging'][0].items() if v]
            episode.set_tag_names(tag_names, request.user)
        return _build_json_response(episode.to_dict(request.user), 201)


class EpisodeListView(View):
    """
    Return serialised subsets of active episodes by tag.
    """
    def get(self, *args, **kwargs):
        tag, subtag = kwargs.get('tag', None), kwargs.get('subtag', None)
        filter_kwargs = {}
        if subtag:
            filter_kwargs['tagging__team__name'] = subtag
        elif tag:
            filter_kwargs['tagging__team__name'] = tag
        # Probably the wrong place to do this, but mine needs specialcasing.
        if tag == 'mine': 
            filter_kwargs['tagging__user'] = self.request.user
        serialised = models.Episode.objects.serialised_active(
            self.request.user, **filter_kwargs)
        return _build_json_response(serialised)


@require_http_methods(['PUT', 'DELETE'])
def subrecord_detail_view(request, model, pk):
    try:
        subrecord = model.objects.get(pk=pk)
    except model.DoesNotExist:
        return HttpResponseNotFound()

    if request.method == 'PUT':
        data = _get_request_data(request)
        try:
            subrecord.update_from_dict(data, request.user)
            return _build_json_response(subrecord.to_dict(request.user))
        except exceptions.ConsistencyError:
            return _build_json_response({'error': 'Item has changed'}, 409)
    elif request.method == 'DELETE':
        subrecord.delete()
        return _build_json_response('')


class TaggingView(View):
    """
    Provide an API for updating the teams to which an episode is
    tagged. 
    """

    def put(self, *args, **kwargs):
        episode = models.Episode.objects.get(pk=kwargs['pk'])
        data = _get_request_data(self.request)
        if 'id' in data:
            data.pop('id')
        tag_names = [n for n, v in data.items() if v]
        episode.set_tag_names(tag_names, self.request.user)
        return _build_json_response(episode.tagging_dict()[0])

    
@require_http_methods(['POST'])
def subrecord_create_view(request, model):
    data = _get_request_data(request)
    subrecord = model()
    if isinstance(subrecord, models.PatientSubrecord):
        episode_id = data['episode_id']
        del data['episode_id']
        patient_id = models.Episode.objects.get(pk=episode_id).patient.pk
        data['patient_id'] = patient_id

    subrecord.update_from_dict(data, request.user)
    return _build_json_response(subrecord.to_dict(request.user), 201)


class EpisodeTemplateView(TemplateView):
    def get_column_context(self, **kwargs):
        """
        Return the context for our columns
        """
        active_schema = self.column_schema

        if 'tag' in kwargs and kwargs['tag'] in LIST_SCHEMAS:
            if 'subtag' in kwargs and kwargs['subtag'] in LIST_SCHEMAS[kwargs['tag']]:
                active_schema = LIST_SCHEMAS[kwargs['tag']][kwargs['subtag']]
            elif 'default' in LIST_SCHEMAS[kwargs['tag']]:
                active_schema = LIST_SCHEMAS[kwargs['tag']]['default']
            else:
                active_schema = LIST_SCHEMAS['default']

        context = []
        for column in active_schema:
            column_context = {}
            name = camelcase_to_underscore(column.__name__)
            column_context['name'] = name
            column_context['title'] = getattr(column, '_title',
                                              name.replace('_', ' ').title())
            column_context['single'] = column._is_singleton
            column_context['episode_category'] = getattr(column, '_episode_category', None)
            column_context['batch_template'] = getattr(column, '_batch_template', None)
            
            list_display_templates = [name + '.html']
            if 'tag' in kwargs:
                list_display_templates.insert(
                    0, 'list_display/{0}/{1}.html'.format(kwargs['tag'], name))
            if 'subtag' in kwargs:
                list_display_templates.insert(
                    0, 'list_display/{0}/{1}/{2}.html'.format(kwargs['subtag'],
                                                              kwargs['tag'],
                                                              name))
            column_context['template_path'] = select_template(list_display_templates).name

            column_context['modal_template_path'] = name + '_modal.html'
            column_context['detail_template_path'] = select_template([name + '_detail.html', name + '.html']).name
            context.append(column_context)

        return context

    def get_context_data(self, **kwargs):
        context = super(EpisodeTemplateView, self).get_context_data(**kwargs)
        # todo rename/refactor this accordingly
        context['teams'] = models.Team.for_user(self.request.user)
        context['columns'] = self.get_column_context(**kwargs)
        if 'tag' in kwargs:
            context['team'] = models.Team.objects.get(name=kwargs['tag'])
        return context


class EpisodeListTemplateView(EpisodeTemplateView):
    template_name = 'episode_list.html'
    column_schema = schema.list_schemas['default']

    
class DischargeListTemplateView(EpisodeTemplateView):
    template_name = 'discharge_list.html'
    column_schema = schema.list_columns

    
class SaveFilterModalView(TemplateView):
    template_name = 'save_filter_modal.html'


class EpisodeDetailTemplateView(EpisodeTemplateView):
    template_name = 'episode_detail.html'
    column_schema = schema.detail_columns


class TagsTemplateView(TemplateView):
    template_name = 'tagging_modal.html'

    def get_context_data(self, **kwargs):
        context = super(TagsTemplateView, self).get_context_data(**kwargs)
        context['teams'] = models.Team.for_user(self.request.user)
        return context


class SearchTemplateView(TemplateView):
    template_name = 'search.html'


class ExtractTemplateView(TemplateView):
    template_name = 'extract.html'

    
class AddEpisodeTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'add_episode_modal.html'

    def get_context_data(self, **kwargs):
        context = super(AddEpisodeTemplateView, self).get_context_data(**kwargs)
        context['teams'] = models.Team.for_user(self.request.user)
        return context

    
class DischargeEpisodeTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'discharge_episode_modal.html'


class DischargeOpatEpisodeTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'discharge_opat_episode_modal.html'


# OPAT specific templates
class OpatReferralTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'opat_referral_modal.html'


class OpatAddEpisodeTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'opat/add_episode_modal.html'


class OpatInternalReferralTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'opat/internal_referral.html'


class DeleteItemConfirmationView(LoginRequiredMixin, TemplateView):
    template_name = 'delete_item_confirmation_modal.html'


class HospitalNumberTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'hospital_number_modal.html'


class ReopenEpisodeTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'reopen_episode_modal.html'


class UndischargeTemplateView(TemplateView):
    template_name = 'undischarge_modal.html'

class IndexView(LoginRequiredMixin, TemplateView):
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['brand_name'] = getattr(settings, 'OPAL_BRAND_NAME', 'OPAL')
        context['settings'] = settings
        if hasattr(settings, 'OPAL_EXTRA_APPLICATION'):
            context['extra_application'] = settings.OPAL_EXTRA_APPLICATION
        return context

    template_name = 'opal.html'

class ModalTemplateView(LoginRequiredMixin, TemplateView):

    def dispatch(self, *a, **kw):
        """
        Set the context for what this modal is for so
        it can be accessed by all subsequent methods
        """
        self.column = kw['model']
        self.name = camelcase_to_underscore(self.column.__name__)
        return super(ModalTemplateView, self).dispatch(*a, **kw)

    def get_template_names(self):
        return [self.name + '_modal.html']

    def get_context_data(self, **kwargs):
        context = super(ModalTemplateView, self).get_context_data(**kwargs)
        context['name'] = self.name
        context['title'] = getattr(self.column, '_title', self.name.replace('_', ' ').title())
        context['single'] = self.column._is_singleton
        return context


class SchemaBuilderView(View):

    def serialize_schema(self, schema):
        cols = []
        for column in schema:
            col = {
                'name': column.get_api_name(),
                'display_name': column.get_display_name(),
                'single': column._is_singleton,
                'fields': column.build_field_schema()
                }
            if hasattr(column, '_sort'):
                col['sort'] = column._sort
            if hasattr(column, '_read_only'):
                col['readOnly'] = column._read_only
            
            cols.append(col)
        return cols

    def _get_plugin_schemas(self):
        scheme = {}
        for plugin in OpalPlugin.__subclasses__():
            scheme.update(plugin().list_schemas())
        return scheme
    
    def _get_serialized_schemas(self, schemas):
        scheme = {}
        for name, s in schemas.items():
            if isinstance(s, list):
                scheme[name] = self.serialize_schema(s)
            else:
                scheme[name] = {}
                for n, c in s.items():
                    scheme[name][n] = self.serialize_schema(c)
        return scheme
    
    def get(self, *args, **kw):
        scheme = self._get_serialized_schemas(self.columns)
        return _build_json_response(scheme)


class ListSchemaView(SchemaBuilderView):
    columns = schema.list_schemas

    def get(self, *args, **kw):
        schema = self._get_serialized_schemas(self._get_plugin_schemas())
        schema.update(self._get_serialized_schemas(self.columns))
        return _build_json_response(schema)


class DetailSchemaView(SchemaBuilderView):
    def get(self, *args, **kw):
        return _build_json_response(self.serialize_schema(schema.detail_columns))


class ExtractSchemaView(SchemaBuilderView):
    def get(self, *args, **kw):
        return _build_json_response(self.serialize_schema(schema.extract_columns))


def check_password_reset(request, *args, **kwargs):
    """
    Check to see if the user needs to reset their password
    """
    response = login(request, *args, **kwargs)
    if response.status_code == 302:
        try:
            profile = request.user.get_profile()
            if profile and profile.force_password_change:
                return redirect('django.contrib.auth.views.password_change')
        except models.UserProfile.DoesNotExist:
            models.UserProfile.objects.create(user=request.user, force_password_change=True)
            return redirect('django.contrib.auth.views.password_change')
    return response


class AccountDetailTemplateView(TemplateView):
    template_name = 'accounts/account_detail.html'


class BannedView(TemplateView):
    template_name = 'accounts/banned.html'

    def get_context_data(self, *a, **k):
        data = super(BannedView, self).get_context_data(*a, **k)
        data['banned'] = banned
        return data


def options_view(request):
    data = {}
    
    for model in LookupList.__subclasses__():
        options = [instance.name for instance in model.objects.all()]
        data[model.__name__.lower()] = options

    for synonym in Synonym.objects.all():
        name = type(synonym.content_object).__name__.lower()
        data[name].append(synonym.name)

    for name in data:
        data[name].sort()

    data['micro_test_defaults'] = micro_test_defaults

    tag_hierarchy = collections.defaultdict(list)
    tag_display = {}
    
    for team in models.Team.for_user(request.user):
        tag_display[team.name] = team.title
        if team.has_subtags:
            for st in team.team_set.all():
                tag_hierarchy[team.name].append(st.name)
                tag_display[st.name] = st.title
        else:
            tag_hierarchy[team.name] = []

    data['tag_hierarchy'] = tag_hierarchy
    data['tag_display'] = tag_display

    return _build_json_response(data)


def userprofile_view(request):
    profile = request.user.get_profile()
    data = dict(
        readonly=profile.readonly,
        can_extract=profile.can_extract,
        filters=[f.to_dict() for f in profile.user.filter_set.all()]
        )
    return _build_json_response(data)


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
                print 'Tagggging'
                print query
                # kw = {'tagging__team__name{0}'.format(contains): query['query']}
                # eps = models.Episode.objects.filter(**kw)
                eps = models.Episode.objects.ever_tagged(query['field'])
                print eps
                

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
        fname = json_to_csv(self.get_episodes(), self.description(), self.request.user)
        resp = HttpResponse(
            open(fname, 'rb').read(),
            mimetype='application/force-download'
            )
        resp['Content-Disposition'] = 'attachment; filename="{0}extract{1}.zip"'.format(
            settings.OPAL_BRAND_NAME, datetime.datetime.now().isoformat())
        return resp


class ReportView(TemplateView):
    """
    Base class for reports.
    """

    def get_data(self):
        return {}

    def get_context_data(self, *a, **kw):
        ctx = super(ReportView, self).get_context_data(*a, **kw)
        ctx.update(self.get_data())
        return ctx


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


class FlowView(View):
    def get(self, *args, **kw):
        return _build_json_response(flow.flows)
