"""
Views for the pathway Opal Plugin
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from opal.core.pathway import Pathway


class PathwayIndexView(LoginRequiredMixin, TemplateView):
    """
    Main entrypoint into the pathway portal service.
    This is the entry point that loads in the pathway.
    """
    template_name = 'pathway/index.html'


class PathwayTemplateView(LoginRequiredMixin, TemplateView):
    def dispatch(self, request, *args, **kwargs):
        self.name = kwargs.get('name', 'pathway')
        self.pathway = Pathway.get(self.name)()
        self.is_modal = request.GET.get("is_modal", False)
        return super(PathwayTemplateView, self).dispatch(
            request, *args, **kwargs
        )

    def get_template_names(self, *args, **kwargs):
        return self.pathway.get_template(self.is_modal)

    def get_context_data(self, *args, **kwargs):
        ctx = super(PathwayTemplateView, self).get_context_data(
            *args, **kwargs
        )
        ctx["pathway"] = self.pathway
        return ctx
