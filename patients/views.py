import json
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from rest_framework import generics, response, status, renderers, views
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

    def post(self, request, *args, **kwargs):
        try:
            hospital_number = request.DATA['demographics']['hospital_number']
            patient = models.Patient.objects.get(demographics__hospital_number=hospital_number)
        except models.Patient.DoesNotExist:
            patient = models.Patient.objects.create()

        location = patient.location
        for field in location._meta.fields:
            field_name = field.name
            if field_name not in ['id', 'patient'] and field_name in request.DATA['location']:
                setattr(location, field_name, request.DATA['location'][field_name])
        location.save()

        demographics = patient.demographics
        for field in demographics._meta.fields:
            field_name = field.name
            if field_name not in ['id', 'patient'] and field_name in request.DATA['demographics']:
                setattr(demographics, field_name, request.DATA['demographics'][field_name])
        demographics.save()

        tags = request.DATA.get('tags', {})
        for tagging in patient.tagging_set.all():
            if not tags.get(tagging.tag_name, False):
                tagging.delete()

        for tag_name, value in tags.items():
            if not value:
                continue
            if tag_name not in [t.tag_name for t in patient.tagging_set.all()]:
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
    template_name = 'opal.html'

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
    template_name = 'contact.html'

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

class SearchView(LoginRequiredMixin, views.APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer, renderers.JSONRenderer]
    serializer_class = serializers.PatientSearchSerializer

    def get_template_names(self):
        return ['search_results.html']

    def get(self, request, *args, **kwargs):
        search_keys = ['hospital_number', 'name']
        search_terms = {key: self.request.GET.get(key, '') for key in search_keys}
        filter_dict = {'demographics__' + key: term for key, term in search_terms.items() if term}
        if filter_dict:
            queryset = models.Patient.objects.filter(**filter_dict)
        else:
            queryset = models.Patient.objects.none()
        serializer = serializers.PatientSearchSerializer(queryset, many=True)
        data = {'patients': serializer.data}

        # We cannot get the tags in the serializer because this requires the user
        for patient in data['patients']:
            taggings = models.Tagging.objects.filter(patient_id=patient['id'])
            patient['tags'] = {t.tag_name: True for t in taggings if t.user is None or t.user == request.user}

        data['search_terms'] = search_terms
        return response.Response(data)
