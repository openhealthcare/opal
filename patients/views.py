from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = "opal.html"

# This probably doesn't belong here
class ContactView(TemplateView):
    template_name = "contact.html"
