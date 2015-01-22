"""
Core OPAL Views
"""
import collections
import datetime
import json

from django.conf import settings
from django.contrib.auth.views import login
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect
from django.template.loader import select_template
from django.template import TemplateDoesNotExist
from django.utils.decorators import method_decorator
from django.utils import formats
from django.views.generic import TemplateView, View
from django.views.decorators.http import require_http_methods

from opal import application
from opal import glossolalia
from opal.utils.http import with_no_caching
from opal.utils import (camelcase_to_underscore, stringport, fields,
                        json_to_csv, OpalPlugin)
from opal.utils.banned_passwords import banned
from opal.utils.models import LookupList, episode_subrecords, patient_subrecords, subrecords
from opal.utils.views import LoginRequiredMixin, _get_request_data, _build_json_response
from opal import models, exceptions

app = application.get_app()

schema = stringport(app.schema_module)
flow = stringport(app.flow_module)
# TODO This is stupid - we can fully deprecate this please?
try:
    options = stringport(settings.OPAL_OPTIONS_MODULE)
    micro_test_defaults = options.micro_test_defaults
except AttributeError:
    class options:
        model_names = []
    micro_test_defaults = []


option_models = models.option_models
Synonym = models.Synonym

LIST_SCHEMAS = {}
for plugin in OpalPlugin.__subclasses__():
    LIST_SCHEMAS.update(plugin().list_schemas())
LIST_SCHEMAS.update(schema.list_schemas.copy())


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

class EpisodeTemplateView(TemplateView):
    def get_column_context(self, **kwargs):
        """
        Return the context for our columns
        """
        from opal.views.templates import _get_column_context
        
        active_schema = self.column_schema
        
        if 'tag' in kwargs and kwargs['tag'] in LIST_SCHEMAS:
            if 'subtag' in kwargs and kwargs['subtag'] in LIST_SCHEMAS[kwargs['tag']]:
                active_schema = LIST_SCHEMAS[kwargs['tag']][kwargs['subtag']]
            elif 'default' in LIST_SCHEMAS[kwargs['tag']]:
                active_schema = LIST_SCHEMAS[kwargs['tag']]['default']
            else:
                active_schema = LIST_SCHEMAS['default']

        return _get_column_context(active_schema, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EpisodeTemplateView, self).get_context_data(**kwargs)
        # TODO rename/refactor this accordingly
        context['teams'] = models.Team.for_user(self.request.user)
        print context['teams']
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


class EpisodeDetailTemplateView(EpisodeTemplateView):
    template_name = 'episode_detail.html'
    column_schema = schema.detail_columns


class TagsTemplateView(TemplateView):
    template_name = 'tagging_modal.html'

    def get_context_data(self, **kwargs):
        context = super(TagsTemplateView, self).get_context_data(**kwargs)
        context['teams'] = models.Team.for_user(self.request.user)
        return context


class AddEpisodeTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'add_episode_modal.html'

    def get_context_data(self, **kwargs):
        context = super(AddEpisodeTemplateView, self).get_context_data(**kwargs)
        context['teams'] = models.Team.for_user(self.request.user)
        return context


class AddEpisodeWithoutTeamsTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'add_episode_modal.html'

    def get_context_data(self, **kwargs):
        context = super(AddEpisodeWithoutTeamsTemplateView, self).get_context_data(**kwargs)
        context['teams'] = []
        return context


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'opal.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['brand_name'] = getattr(settings, 'OPAL_BRAND_NAME', 'OPAL')
        context['settings'] = settings
        if hasattr(settings, 'OPAL_EXTRA_APPLICATION'):
            context['extra_application'] = settings.OPAL_EXTRA_APPLICATION
        return context


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

class UserProfileView(LoginRequiredMixin, View):
    """
    Render a serialized version of the currently logged in user's
    userprofile.
    """
    def get(self, *args, **kw):
        profile = self.request.user.get_profile()
        data = dict(
            readonly=profile.readonly,
            can_extract=profile.can_extract,
            filters=[f.to_dict() for f in profile.user.filter_set.all()],
            roles=profile.get_roles()
            )
        return _build_json_response(data)

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


"""Internal (Legacy) API Views"""

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
        pre = episode.to_dict(request.user)
        episode.update_from_dict(data, request.user)
        post = episode.to_dict(request.user)
        glossolalia.change(pre, post)
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

        location = episode.location_set.get()
        location.update_from_dict(data['location'], request.user)
        if 'tagging' in data:
            tag_names = [n for n, v in data['tagging'][0].items() if v]
            episode.set_tag_names(tag_names, request.user)

        serialised = episode.to_dict(request.user)
        glossolalia.admit(serialised)
        return _build_json_response(serialised, 201)


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

    
class EpisodeCopyToCategoryView(LoginRequiredMixin, View):
    """
    Copy an episode to a given category, excluding tagging.   
    """
    def post(self, args, pk=None, category=None, **kwargs):
        old = models.Episode.objects.get(pk=pk)
        new = models.Episode(patient=old.patient, 
                             date_of_admission=old.date_of_admission)
        new.save()
        for sub in episode_subrecords():
            if sub._is_singleton:
                continue
            for item in sub.objects.filter(episode=old):
                item.id = None
                item.episode = new
                item.save()
        serialised = new.to_dict(self.request.user)
        glossolalia.admit(serialised)
        return _build_json_response(serialised)

        
@require_http_methods(['PUT', 'DELETE'])
def subrecord_detail_view(request, model, pk):
    try:
        subrecord = model.objects.get(pk=pk)
    except model.DoesNotExist:
        return HttpResponseNotFound()

    try:
        pre = subrecord.episode.to_dict(request.user)
    except AttributeError:
        pre = subrecord.patient.to_dict(request.user)
        
    if request.method == 'PUT':
        data = _get_request_data(request)
        try:
            subrecord.update_from_dict(data, request.user)
            
            try:
                post = subrecord.episode.to_dict(request.user)
            except AttributeError:
                post = subrecord.patient.to_dict(request.user)
            glossolalia.change(pre, post)

            return _build_json_response(subrecord.to_dict(request.user))
        except exceptions.ConsistencyError:
            return _build_json_response({'error': 'Item has changed'}, 409)
    elif request.method == 'DELETE':
        subrecord.delete()
        try:
            post = subrecord.episode.to_dict(request.user)
        except AttributeError:
            post = subrecord.patient.to_dict(request.user)
        glossolalia.change(pre, post)
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
        pre = episode.to_dict(self.request.user)
        episode.set_tag_names(tag_names, self.request.user)
        post = episode.to_dict(self.request.user)
        glossolalia.transfer(pre, post)
        return _build_json_response(episode.tagging_dict(self.request.user)[0])


@require_http_methods(['POST'])
def subrecord_create_view(request, model):
    data = _get_request_data(request)
    subrecord = model()

    episode_id = data['episode_id']
    episode = models.Episode.objects.get(pk=episode_id)
    pre = episode.to_dict(request.user)

    if isinstance(subrecord, models.PatientSubrecord):
        del data['episode_id']
        patient_id = episode.patient.pk
        data['patient_id'] = patient_id

    subrecord.update_from_dict(data, request.user)

    episode = models.Episode.objects.get(pk=episode_id)
    post = episode.to_dict(request.user)
    glossolalia.change(pre, post)
    return _build_json_response(subrecord.to_dict(request.user), 201)




class SchemaBuilderView(View):

    def serialize_model(self, model):
        col = {
            'name': model.get_api_name(),
            'display_name': model.get_display_name(),
            'single': model._is_singleton,
            'fields': model.build_field_schema()
            }
        if hasattr(model, '_sort'):
            col['sort'] = model._sort
        if hasattr(model, '_read_only'):
            col['readOnly'] = model._read_only
        return col

    def serialize_schema(self, schema):
        return [self.serialize_model(column) for column in schema]

    def _get_plugin_schemas(self):
        scheme = {}
        for plugin in OpalPlugin.__subclasses__():
            scheme.update(plugin().list_schemas())
        return scheme

    def _get_list_schema(self):
        schemas = self._get_field_names(self.columns)

        plugin_schemas = self._get_plugin_schemas()
        schemas.update(self._get_field_names(plugin_schemas))
        return schemas

    def _get_detail_schema(self):
        return self.serialize_schema(schema.detail_columns)

    def _get_field_names(self, schemas):
        scheme = {}
        for name, s in schemas.items():
            if isinstance(s, list):
                try:
                    scheme[name] = [f.get_api_name() for f in s]
                except:
                    raise
            else:
                scheme[name] = self._get_field_names(s)
                # scheme[name] = {}
                # for n, c in s.items():
                #     scheme[name][n] = [f.get_api_name() for f in c]
        return scheme

    def _get_all_fields(self):
        response = {
            subclass.get_api_name(): self.serialize_model(subclass) 
            for subclass in subrecords()
        }
        response['tagging'] = self.serialize_model(models.Tagging)
        return response

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
        response = {}
        response['fields'] = self._get_all_fields()
        response['list_schema'] = self._get_list_schema()
        return _build_json_response(response)


class DetailSchemaView(SchemaBuilderView):
    def get(self, *args, **kw):
        response = dict(
            fields=self._get_all_fields(), 
            detail_schema=self._get_detail_schema()
        )
        return _build_json_response(response)


class ExtractSchemaView(SchemaBuilderView):
    def get(self, *args, **kw):
        return _build_json_response(self.serialize_schema(schema.extract_columns))




class OptionsView(View):
    def get(self, *args, **kwargs):
        data = {}
        for model in LookupList.__subclasses__():
            options = [instance.name for instance in model.objects.all()]
            data[model.__name__.lower()] = options

        for synonym in Synonym.objects.all():
            try:
                co =  synonym.content_object
            except AttributeError:
                continue
            name = type(co).__name__.lower()
            data[name].append(synonym.name)

        for name in data:
            data[name].sort()

        data['micro_test_defaults'] = micro_test_defaults

        tag_hierarchy = collections.defaultdict(list)
        tag_display = {}

        if self.request.user.is_authenticated():
            teams = models.Team.for_user(self.request.user)
            for team in teams:
                if team.parent:
                    continue # Will be filled in at the appropriate point! 
                tag_display[team.name] = team.title

                subteams = [st for st in teams if st.parent == team]
                tag_hierarchy[team.name] = [st.name for st in subteams]
                for sub in subteams: 
                    tag_display[sub.name] = sub.title

        data['tag_hierarchy'] = tag_hierarchy
        data['tag_display'] = tag_display

        data['macros'] = models.Macro.to_dict()

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
        fname = json_to_csv(self.get_episodes(), self.description(), self.request.user)
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


class FlowView(View):
    """
    API call to retrieve the patient flow routes for this instance
    """
    def get(self, *args, **kw):
        """
        Return a dictionary of flow objects - these will be of the form:

        { team: {verb: { controller: 'XXXX', template: 'XXXX'} } }

        This allows the Flow service to determine the correct Angular 
        controller for any given episode.
        """
        flows = {}
        for plugin in OpalPlugin.__subclasses__():
            flows.update(plugin().flows())
        flows.update(flow.flows)
        return _build_json_response(flows)
