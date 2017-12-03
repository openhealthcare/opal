"""
Module entrypoint for core Opal views
"""
from django.contrib.auth.views import login
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.views.generic import TemplateView, View

from opal import models
from opal.core import application, detail, episodes
from opal.core.patient_lists import PatientList, TabbedPatientListGroup
from opal.core.subrecords import (
    episode_subrecords, get_subrecord_from_api_name
)
from opal.core.views import LoginRequiredMixin, json_response
from opal.utils import camelcase_to_underscore
from opal.utils.banned_passwords import banned

app = application.get_app()

Synonym = models.Synonym


class PatientListTemplateView(LoginRequiredMixin, TemplateView):

    def dispatch(self, *args, **kwargs):
        try:
            self.patient_list = PatientList.get(kwargs['slug'])
        except ValueError:
            self.patient_list = None
        return super(PatientListTemplateView, self).dispatch(*args, **kwargs)

    def get_column_context(self, **kwargs):
        """
        Return the context for our columns
        """
        # we use this view to load blank tables without content for
        # the list redirect view, so if there are no kwargs, just
        # return an empty context
        if not self.patient_list:
            return []

        return self.patient_list.schema_to_dicts()

    def get_context_data(self, **kwargs):
        context = super(
            PatientListTemplateView, self
        ).get_context_data(**kwargs)
        list_slug = None
        if self.patient_list:
            list_slug = self.patient_list.get_slug()
        context['list_slug'] = list_slug
        context['patient_list'] = self.patient_list
        context['lists'] = list(PatientList.for_user(self.request.user))
        context['num_lists'] = len(context['lists'])

        context['list_group'] = None
        if self.patient_list:
            group = TabbedPatientListGroup.for_list(self.patient_list)
            if group:
                if group.visible_to(self.request.user):
                    context['list_group'] = group

        context['columns'] = self.get_column_context(**kwargs)
        return context

    def get_template_names(self):
        if self.patient_list:
            return self.patient_list().get_template_names()
        return [PatientList.template_name]


class PatientDetailTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'patient_detail.html'

    def get_context_data(self, **kwargs):
        context = super(
            PatientDetailTemplateView, self
        ).get_context_data(**kwargs)

        # django likes to try and initialise classes, even when we
        # don't want it to, so vars it
        context['episode_categories'] = [
            vars(i) for i in episodes.EpisodeCategory.list()
        ]

        # We cast this to a list because it's a generator but we want to
        # consume it twice in the template
        context['detail_views'] = list(
            detail.PatientDetailView.for_user(self.request.user)
        )
        return context


# TODO: ?Remove this ?
class EpisodeDetailTemplateView(LoginRequiredMixin, TemplateView):
    def get(self, *args, **kwargs):
        self.episode = get_object_or_404(models.Episode, pk=kwargs['pk'])
        return super(EpisodeDetailTemplateView, self).get(*args, **kwargs)

    def get_template_names(self):
        names = [
            'detail/{0}.html'.format(self.episode.category_name.lower()),
            'detail/default.html'
        ]
        return names

    def get_context_data(self, **kwargs):
        context = super(
            EpisodeDetailTemplateView, self
        ).get_context_data(**kwargs)
        return context


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'opal.html'


def check_password_reset(request, *args, **kwargs):
    """
    Check to see if the user needs to reset their password
    """
    response = login(request, *args, **kwargs)
    if response.status_code == 302:
        try:
            profile = request.user.profile
            if profile and profile.force_password_change:
                return redirect(
                    'django.contrib.auth.views.password_change'
                )
        except models.UserProfile.DoesNotExist:
            # TODO: This probably doesn't do any harm, but
            # we should really never reach this. Creation
            # of profiles shouldn't happen in a random view.
            models.UserProfile.objects.create(
                user=request.user, force_password_change=True)
            return redirect(
                'django.contrib.auth.views.password_change'
            )
    return response


"""Internal (Legacy) API View"""


class EpisodeCopyToCategoryView(LoginRequiredMixin, View):
    """
    Copy an episode to a given category, excluding tagging.
    """
    def post(self, request, pk=None, category=None, **kwargs):
        old = models.Episode.objects.get(pk=pk)
        new = models.Episode(patient=old.patient,
                             category_name=category,
                             start=old.start)
        new.save()

        for sub in episode_subrecords():
            if sub._is_singleton or not sub._clonable:
                continue
            for item in sub.objects.filter(episode=old):
                item.id = None
                item.episode = new
                item.save()
        serialised = new.to_dict(self.request.user)
        return json_response(serialised)


"""
Template views for Opal
"""


class FormTemplateView(LoginRequiredMixin, TemplateView):
    """
    This view renders the form template for our field.

    These are generated for subrecords, but can also be used
    by plugins for other mdoels.
    """
    template_name = "form_base.html"

    def get_context_data(self, *args, **kwargs):
        ctx = super(FormTemplateView, self).get_context_data(*args, **kwargs)
        ctx["form_name"] = self.column.get_form_template()
        return ctx

    def dispatch(self, *a, **kw):
        """
        Set the context for what this modal is for so
        it can be accessed by all subsequent methods
        """
        self.column = get_subrecord_from_api_name(kw['model'])
        self.name = camelcase_to_underscore(self.column.__name__)
        return super(FormTemplateView, self).dispatch(*a, **kw)


class ModalTemplateView(LoginRequiredMixin, TemplateView):
    def get_template_from_model(self):
        list_prefixes = None

        if self.list_slug:
            patient_list = PatientList.get(self.list_slug)()
            list_prefixes = patient_list.get_template_prefixes()
        return self.column.get_modal_template(
            prefixes=list_prefixes
        )

    def dispatch(self, *a, **kw):
        """
        Set the context for what this modal is for so
        it can be accessed by all subsequent methods
        """
        self.column = kw['model']
        self.list_slug = kw.get('list', None)
        self.template_name = self.get_template_from_model()
        if self.template_name is None:
            raise ValueError(
                'No modal Template available for {0}'.format(
                    self.column.__name__
                )
            )
        self.name = camelcase_to_underscore(self.column.__name__)
        return super(ModalTemplateView, self).dispatch(*a, **kw)

    def get_context_data(self, **kwargs):
        context = super(ModalTemplateView, self).get_context_data(**kwargs)
        context['name'] = self.name
        context['title'] = getattr(
            self.column, '_title', self.name.replace('_', ' ').title()
        )
        context['icon'] = getattr(self.column, '_icon', '')
        # pylint: disable=W0201
        context['single'] = self.column._is_singleton
        context["column"] = self.column

        return context


class RecordTemplateView(LoginRequiredMixin, TemplateView):
    def get_template_names(self):
        model = get_subrecord_from_api_name(self.kwargs["model"])
        template_name = model.get_display_template()
        return [template_name]


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


class UndischargeTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'undischarge_modal.html'


class DischargeEpisodeTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'discharge_episode_modal.html'


class CopyToCategoryTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'copy_to_category.html'


class DeleteItemConfirmationView(LoginRequiredMixin, TemplateView):
    template_name = 'delete_item_confirmation_modal.html'


class RawTemplateView(LoginRequiredMixin, TemplateView):
    """
    Failover view for templates - just look for this path in Django!
    """
    def get(self, *args, **kw):
        self.template_name = kw['template_name']
        try:
            get_template(self.template_name)
        except TemplateDoesNotExist:
            return HttpResponseNotFound()
        return super(RawTemplateView, self).get(*args, **kw)
