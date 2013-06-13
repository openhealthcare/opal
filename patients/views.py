import json
from django.http import HttpResponse
from django.views.generic import TemplateView
from rest_framework import generics
from utils import camelcase_to_underscore
from patients import models, serializers, schema

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
        return getattr(self.patient, camelcase_to_underscore(self.model.__name__)).get(pk=self.kwargs['id'])

class IndexView(TemplateView):
    template_name = "opal.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['columns'] = []

        for column in schema.columns:
            column_context = {}
            name = camelcase_to_underscore(column.__name__)
            column_context['name'] = name
            column_context['title'] = getattr(column, '_title', name.replace('_', ' ').title())
            column_context['single'] = issubclass(column, models.SingletonSubrecord)
            column_context['template_path'] = name + '.html'
            column_context['modal_template_path'] = name + '_modal.html'
            context['columns'].append(column_context)

        return context

# This probably doesn't belong here
class ContactView(TemplateView):
    template_name = "contact.html"

def schema_view(request):
    data = []
    for column in schema.columns:
        data.append({
            'name': camelcase_to_underscore(column.__name__),
            'single': issubclass(column, models.SingletonSubrecord)
        })
    return HttpResponse(json.dumps(data), mimetype='application/json')
