from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = "opal.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['columns'] = [
            {'name': 'location', 'title': 'Location', 'single': 'yes'},
            {'name': 'demographics', 'title': 'Demographics', 'single': 'yes'}, 
            {'name': 'diagnosis', 'title': 'Diagnosis', 'single': 'no'},
            {'name': 'pastMedicalHistory', 'title': 'Past Medical History', 'single': 'no'},
            {'name': 'generalNotes', 'title': 'Notes', 'single': 'no'},
            {'name': 'travel', 'title': 'Travel', 'single': 'no'},
            {'name': 'antimicrobials', 'title': 'Antimicrobials', 'single': 'no'},
            {'name': 'microbiology', 'title': 'Microbiology Results', 'single': 'no'},
            {'name': 'microbiologyComments', 'title': 'Microbiology Input', 'single': 'no'},
            {'name': 'plan', 'title': 'Plan', 'single': 'yes'},
            {'name': 'discharge', 'title': 'Discharge', 'single': 'yes'},
        ]
        for column in context['columns']:
            column['template_path'] = column['name'] + '.html'
            column['modal_template_path'] = column['name'] + '-modal.html'

        return context

# This probably doesn't belong here
class ContactView(TemplateView):
    template_name = "contact.html"
