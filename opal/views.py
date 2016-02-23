"""
Module entrypoint for core OPAL views
"""
from django.conf import settings
from django.contrib.auth.views import login
from django.http import HttpResponseNotFound
from django.shortcuts import redirect
from django.template.loader import select_template, get_template
from django.template import TemplateDoesNotExist
from django.views.generic import TemplateView, View
from django.views.decorators.http import require_http_methods

from opal import models
from opal.core import application, exceptions, glossolalia
from opal.core.subrecords import episode_subrecords, subrecords
from opal.core.views import LoginRequiredMixin, _get_request_data, _build_json_response
from opal.core.schemas import get_all_list_schema_classes
from opal.utils import camelcase_to_underscore, stringport
from opal.utils.banned_passwords import banned

app = application.get_app()

schema = stringport(app.schema_module)
# TODO This is stupid - we can fully deprecate this please?
try:
    options = stringport(settings.OPAL_OPTIONS_MODULE)
    micro_test_defaults = options.micro_test_defaults
except AttributeError:
    class options:
        micro_test_defaults = []

Synonym = models.Synonym


class EpisodeTemplateView(TemplateView):
    def get_column_context(self, **kwargs):
        """
        Return the context for our columns
        """
        active_schema = self.column_schema
        all_list_schemas = get_all_list_schema_classes()
        if 'tag' in kwargs and kwargs['tag'] in all_list_schemas:
            if 'subtag' in kwargs and kwargs['subtag'] in all_list_schemas[kwargs['tag']]:
                active_schema = all_list_schemas[kwargs['tag']][kwargs['subtag']]
            elif 'default' in all_list_schemas[kwargs['tag']]:
                active_schema = all_list_schemas[kwargs['tag']]['default']
            else:
                active_schema = all_list_schemas['default']

        return _get_column_context(active_schema, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EpisodeTemplateView, self).get_context_data(**kwargs)
        teams = models.Team.for_user(self.request.user)
        context['teams'] = teams
        context['columns'] = self.get_column_context(**kwargs)
        if 'tag' in kwargs:
            try:
                context['team'] = models.Team.objects.get(name=kwargs['tag'])
            except models.Team.DoesNotExist:
                context['team'] = None

        context['models'] = { m.__name__: m for m in subrecords() }
        return context


class EpisodeListTemplateView(EpisodeTemplateView):
    template_name = 'episode_list.html'
    column_schema = schema.list_schemas['default']


class EpisodeDetailTemplateView(TemplateView):
    def get(self, *args, **kwargs):
        self.episode = models.Episode.objects.get(pk=kwargs['pk'])
        return super(EpisodeDetailTemplateView, self).get(*args, **kwargs)

    def get_template_names(self):
        names = ['detail/{0}.html'.format(self.episode.category.lower()), 'detail/default.html']
        return names

    def get_context_data(self, **kwargs):
        context = super(EpisodeDetailTemplateView, self).get_context_data(**kwargs)
        context['models'] = { m.__name__: m for m in subrecords() }
        return context


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
            profile = request.user.profile
            if profile and profile.force_password_change:
                return redirect('django.contrib.auth.views.password_change')
        except models.UserProfile.DoesNotExist:
            models.UserProfile.objects.create(user=request.user, force_password_change=True)
            return redirect('django.contrib.auth.views.password_change')
    return response


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
        filter_kwargs = {"tagging__archived": False}
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
                             category=category,
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

"""
Template views for OPAL
"""

def _get_column_context(schema, **kwargs):
    context = []
    for column in schema:
        column_context = {}
        name = camelcase_to_underscore(column.__name__)
        column_context['name'] = name
        column_context['title'] = getattr(column, '_title',
                                          name.replace('_', ' ').title())
        column_context['single'] = column._is_singleton
        column_context['icon'] = getattr(column, '_icon', '')
        column_context['list_limit'] = getattr(column, '_list_limit', None)

        header_templates = [name + '_header.html']
        if 'tag' in kwargs:
            header_templates.insert(
                0, 'list_display/{0}/{1}_header.html'.format(kwargs['tag'], name))
            if 'subtag' in kwargs:
                header_templates.insert(
                    0, 'list_display/{0}/{1}/{2}_header.html'.format(kwargs['tag'],
                                                                     kwargs['subtag'],
                                                                     name))

        column_context['template_path'] = column.get_display_template(
            team=kwargs.get('tag', None), subteam=kwargs.get('subtag', None))

        column_context['detail_template_path'] = select_template([
            t.format(name) for t in '{0}_detail.html', '{0}.html', 'records/{0}.html'
        ]).template.name

        try:
            column_context['header_template_path'] = select_template(header_templates).template.name
        except TemplateDoesNotExist:
            column_context['header_template_path'] = ''

        context.append(column_context)

    return context


class ModalTemplateView(LoginRequiredMixin, TemplateView):
    """
    This view renders the form/modal template for our field.

    These are generated for subrecords, but can also be used
    by plugins for other mdoels.
    """
    def dispatch(self, *a, **kw):
        """
        Set the context for what this modal is for so
        it can be accessed by all subsequent methods
        """
        self.column = kw['model']
        self.tag = kw.get('tag', None)
        self.subtag = kw.get('sub', None)
        self.template_name = self.column.get_form_template(team=self.tag, subteam=self.subtag)
        self.name = camelcase_to_underscore(self.column.__name__)
        return super(ModalTemplateView, self).dispatch(*a, **kw)

    def get_context_data(self, **kwargs):
        context = super(ModalTemplateView, self).get_context_data(**kwargs)
        context['name'] = self.name
        context['title'] = getattr(self.column, '_title', self.name.replace('_', ' ').title())
        # pylint: disable=W0201
        context['single'] = self.column._is_singleton

        return context


class AccountDetailTemplateView(TemplateView):
    template_name = 'accounts/account_detail.html'


class BannedView(TemplateView):
    template_name = 'accounts/banned.html'

    def get_context_data(self, *a, **k):
        data = super(BannedView, self).get_context_data(*a, **k)
        data['banned'] = banned
        return data

class HospitalNumberTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'hospital_number_modal.html'


class ReopenEpisodeTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'reopen_episode_modal.html'


class UndischargeTemplateView(TemplateView):
    template_name = 'undischarge_modal.html'

class DischargeEpisodeTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'discharge_episode_modal.html'


class CopyToCategoryTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'copy_to_category.html'


class DeleteItemConfirmationView(LoginRequiredMixin, TemplateView):
    template_name = 'delete_item_confirmation_modal.html'


class RawTemplateView(TemplateView):
    """
    Failover view for templates - just look for this path in Django!
    """
    def dispatch(self, *args, **kw):
        self.template_name = kw['template_name']
        try:
            get_template(self.template_name)
        except TemplateDoesNotExist:
            return HttpResponseNotFound()
        return super(RawTemplateView, self).dispatch(*args, **kw)
