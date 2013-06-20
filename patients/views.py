import json
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from rest_framework import generics, response, status
from utils import camelcase_to_underscore
from patients import models, serializers, schema
from options.models import option_models

class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)

class SingletonMixin(object):
    def get_serializer_class(self):
        return serializers.build_subrecord_serializer(self.model)

    @property
    def patient(self):
        return models.Patient.objects.get(pk=self.kwargs['patient_id'])

class PatientList(LoginRequiredMixin, generics.ListAPIView):
    serializer_class = serializers.PatientSerializer

    def get_queryset(self):
        tag = self.request.GET.get('tag', 'mine')
        if tag == 'mine':
            return models.Patient.objects.filter(tagging__user=self.request.user)
        else:
            return models.Patient.objects.filter(tagging__tag_name=tag)

    # TODO use DRF for this
    def post(self, request, *args, **kwargs):
        patient = models.Patient.objects.create()
        location = patient.location
        location.__dict__.update(request.DATA['location'])
        location.save()
        demographics = patient.demographics
        demographics.__dict__.update(request.DATA['demographics'])
        demographics.save()
        for tag_name in request.DATA.get('tags', []):
            tagging = models.Tagging(tag_name=tag_name)
            if tag_name == 'mine':
                tagging.user = request.user
            patient.tagging_set.add(tagging)

        serializer = serializers.PatientSerializer(patient)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED)

class SingletonSubrecordDetail(LoginRequiredMixin, SingletonMixin, generics.RetrieveUpdateAPIView):
    def get_object(self, queryset=None):
        return getattr(self.patient, self.model.__name__.lower())

class SubrecordList(LoginRequiredMixin, SingletonMixin, generics.ListCreateAPIView):
    pass

class SubrecordDetail(LoginRequiredMixin, SingletonMixin, generics.RetrieveUpdateDestroyAPIView):
    def get_object(self, queryset=None):
        return getattr(self.patient, camelcase_to_underscore(self.model.__name__)).get(pk=self.kwargs['id'])

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "opal.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['tags'] = models.TAGS

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
    columns = []
    for column in schema.columns:
        columns.append({
            'name': camelcase_to_underscore(column.__name__),
            'single': issubclass(column, models.SingletonSubrecord)
        })
    option_lists = {}
    for name, model in option_models.items():
        synonyms = []
        for instance in model.objects.all():
            synonyms.append([instance.name, instance.name])
            for synonym in instance.synonyms.all():
                synonyms.append([synonym.name, instance.name])
        option_lists[name] = synonyms
    data = {
        'columns': columns,
        'option_lists': option_lists
    }
    return HttpResponse(json.dumps(data), mimetype='application/json')
