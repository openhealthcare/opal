"""
OPAL Viewz!
"""
import json
import datetime

from django.contrib.auth.views import login
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic import TemplateView, View
from django.views.decorators.http import require_http_methods
from django.template.loader import select_template
from django.utils.decorators import method_decorator
from django.utils import formats
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from opal.utils.http import with_no_caching
from opal.utils import camelcase_to_underscore, stringport
from opal.utils.banned_passwords import banned
from opal import models, exceptions

schema = stringport(settings.OPAL_SCHEMA_MODULE)
options = stringport(settings.OPAL_OPTIONS_MODULE)
micro_test_defaults = options.micro_test_defaults
option_models = models.option_models
Synonym = models.Synonym
tags = stringport(settings.OPAL_TAGS_MODULE)
TAGS = tags.TAGS

def _get_request_data(request):
    data = request.read()
    return json.loads(data)

def _build_json_response(data, status_code=200):
    response = HttpResponse()
    response['Content-Type'] = 'application/json'
    response.content = json.dumps(data, cls=DjangoJSONEncoder)
    response.status_code = status_code
    return response


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)

@require_http_methods(['GET', 'PUT'])
def episode_detail_view(request, pk):
    try:
        episode = models.Episode.objects.get(pk=pk)
    except models.Episode.DoesNotExist:
        return HttpResponseNotFound()

    if request.method == 'GET':
        return _build_json_response(episode.to_dict(request.user))

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
        episodes = models.Episode.objects.filter(active=True)
        return _build_json_response([episode.to_dict(request.user)
                                     for episode in episodes])

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
            return _build_json_response({'error': 'Patient already has active episode'}, 400)

        episode.update_from_location_dict(data['location'], request.user)
        return _build_json_response(episode.to_dict(request.user), 201)

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

@require_http_methods(['POST'])
def subrecord_create_view(request, model):
    subrecord = model()
    data = _get_request_data(request)
    subrecord.update_from_dict(data, request.user)
    return _build_json_response(subrecord.to_dict(request.user), 201)

class EpisodeTemplateView(TemplateView):
    def get_column_context(self):
        """
        Return the context for our columns
        """
        context = []
        for column in self.column_schema:
            column_context = {}
            name = camelcase_to_underscore(column.__name__)
            column_context['name'] = name
            column_context['title'] = getattr(column, '_title',
                                              name.replace('_', ' ').title())
            column_context['single'] = column._is_singleton
            column_context['template_path'] = name + '.html'
            column_context['modal_template_path'] = name + '_modal.html'
            column_context['detail_template_path'] = select_template([name + '_detail.html', name + '.html']).name
            context.append(column_context)
        return context

    def get_context_data(self, **kwargs):
        context = super(EpisodeTemplateView, self).get_context_data(**kwargs)
        context['tags'] = TAGS
        context['columns'] = self.get_column_context()
        return context


class EpisodeListTemplateView(EpisodeTemplateView):
    template_name = 'episode_list.html'
    column_schema = schema.list_columns


class EpisodeDetailTemplateView(EpisodeTemplateView):
    template_name = 'episode_detail.html'
    column_schema = schema.detail_columns


class SearchTemplateView(TemplateView):
    template_name = 'search.html'

    def get_context_data(self, **kwargs):
        context = super(SearchTemplateView, self).get_context_data(**kwargs)
        context['tags'] = TAGS
        return context

class AddEpisodeTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'add_episode_modal.html'

    def get_context_data(self, **kwargs):
        context = super(AddEpisodeTemplateView, self).get_context_data(**kwargs)
        context['tags'] = TAGS
        return context

class DischargeEpisodeTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'discharge_episode_modal.html'


class DeleteItemConfirmationView(LoginRequiredMixin, TemplateView):
    template_name = 'delete_item_confirmation_modal.html'


class HospitalNumberTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'hospital_number_modal.html'


class ReopenEpisodeTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'reopen_episode_modal.html'


class IndexView(LoginRequiredMixin, TemplateView):
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['brand_name'] = getattr(settings, 'OPAL_BRAND_NAME', 'OPAL')
        return context

    template_name = 'opal.html'

class ModalTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'modal_base.html'

    def get_context_data(self, **kwargs):
        context = super(ModalTemplateView, self).get_context_data(**kwargs)
        column = self.kwargs['model']
        name = camelcase_to_underscore(column.__name__)

        context['name'] = name
        context['title'] = getattr(column, '_title', name.replace('_', ' ').title())
        context['single'] = column._is_singleton
        context['modal_template_path'] = name + '_modal.html'

        if name == 'location':
            context['tags'] = TAGS

        return context

# This probably doesn't belong here
class ContactView(TemplateView):
    template_name = 'contact.html'


class SchemaBuilderView(View):
    def get(self, *args, **kw):
        cols = []
        for column in self.columns:
            col = {
                'name': column.get_api_name(),
                'single': column._is_singleton,
                'fields': column.build_field_schema()
                }
            if hasattr(column, '_sort'):
                col['sort'] = column._sort
            cols.append(col)
        return _build_json_response(cols)


class ListSchemaView(SchemaBuilderView):
    columns = schema.list_columns


class DetailSchemaView(SchemaBuilderView):
    columns = schema.detail_columns


def check_password_reset(request, *args, **kwargs):
    """
    Check to see if the user needs to reset their password
    """
    response = login(request, *args, **kwargs)
    if response.status_code == 302:
        try:
            profile = request.user.get_profile()
            print profile
            if profile and profile.force_password_change:
                return redirect('django.contrib.auth.views.password_change')
        except models.UserProfile.DoesNotExist:
            print 'creatin'
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
    for name, model in option_models.items():
        options = [instance.name for instance in model.objects.all()]
        data[name] = options

    for synonym in Synonym.objects.all():
        name = type(synonym.content_object).__name__.lower()
        data[name].append(synonym.name)

    for name in data:
        data[name].sort()

    data['micro_test_defaults'] = micro_test_defaults

    tag_hierarchy = {}
    tag_display = {}
    for tag in TAGS:
        tag_display[tag.name] = tag.title
        if tag.subtags:
            tag_hierarchy[tag.name] = [st.name for st in tag.subtags]
            for t in tag.subtags:
                tag_display[t.name] = t.title
        else:
            tag_hierarchy[tag.name] = []
    data['tag_hierarchy'] = tag_hierarchy
    data['tag_display'] = tag_display

    return _build_json_response(data)
