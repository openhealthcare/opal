"""
Template views for OPAL
"""
from django.views.generic import TemplateView

from opal.utils.views import LoginRequiredMixin, _get_request_data, _build_json_response

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
