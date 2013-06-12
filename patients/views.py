from django.views.generic import TemplateView
from rest_framework import generics
from patients import models, serializers

class PatientList(generics.ListCreateAPIView):
    queryset = models.Patient.objects.all()
    serializer_class = serializers.PatientSerializer

class SingletonView(object):
    def get_serializer_class(self):
        return serializers.build_subrecord_serializer(self.model)

    @property
    def patient(self):
        return models.Patient.objects.get(pk=self.kwargs['patient_id'])

class SingletonSubrecordDetail(SingletonView, generics.RetrieveUpdateAPIView):
    def get_object(self, queryset=None):
        return getattr(self.patient, self.model.__name__.lower())

class SubrecordList(SingletonView, generics.ListCreateAPIView):
    pass

class SubrecordDetail(SingletonView, generics.RetrieveUpdateAPIView):
    def get_object(self, queryset=None):
        return getattr(self.patient, self.model.__name__.lower() + '_set').get(pk=self.kwargs['id'])

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
