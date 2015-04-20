"""
Template views for OPAL
"""
from django.template import TemplateDoesNotExist
from django.template.loader import select_template, get_template
from django.views.generic import TemplateView

from opal.utils import camelcase_to_underscore
from opal.utils.views import LoginRequiredMixin, _get_request_data, _build_json_response
from opal.utils.banned_passwords import banned

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
        column_context['batch_template'] = getattr(column, '_batch_template', None)

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
        ]).name

        try:
            column_context['header_template_path'] = select_template(header_templates).name
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


class SaveFilterModalView(TemplateView):
    template_name = 'save_filter_modal.html'

class SearchTemplateView(TemplateView):
    template_name = 'search.html'

class ExtractTemplateView(TemplateView):
    template_name = 'extract.html'


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
