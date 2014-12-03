"""
Template views for OPAL
"""
from django.template import TemplateDoesNotExist
from django.template.loader import select_template, get_template
from django.views.generic import TemplateView

from opal.utils import camelcase_to_underscore
from opal.utils.views import LoginRequiredMixin, _get_request_data, _build_json_response

def _get_column_context(schema, **kwargs):
    context = []
    for column in schema:
        column_context = {}
        name = camelcase_to_underscore(column.__name__)
        column_context['name'] = name
        column_context['title'] = getattr(column, '_title',
                                          name.replace('_', ' ').title())
        column_context['single'] = column._is_singleton
        column_context['episode_category'] = getattr(column, '_episode_category', None)
        column_context['episode_category_excludes'] = getattr(column, '_episode_category_excludes', None)
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

        
        header_template = '_{0}_header.html'.format(name)
        try:
            column_context['header_template_path'] = get_template(header_template).name
        except TemplateDoesNotExist:
            column_context['header_template_path'] = ''

        context.append(column_context)

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


class DischargeOpatEpisodeTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'discharge_opat_episode_modal.html'


# OPAT specific templates
class OpatReferralTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'opat_referral_modal.html'


class OpatAddEpisodeTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'opat/add_episode_modal.html'


class CopyToCategoryTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'copy_to_category.html'


class DeleteItemConfirmationView(LoginRequiredMixin, TemplateView):
    template_name = 'delete_item_confirmation_modal.html'
