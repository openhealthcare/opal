import json
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from rest_framework import generics, response, status, renderers, views
from utils import camelcase_to_underscore
from patients import models, serializers, schema
from options.models import option_models, Synonym

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
        tag = self.request.GET.get('tag')
        if tag is None:
            return models.Patient.objects.all()
        elif tag == 'mine':
            return models.Patient.objects.filter(tagging__user=self.request.user)
        else:
            return models.Patient.objects.filter(tagging__tag_name=tag)

    def get(self, request, *args, **kwargs):
        response = super(PatientList, self).get(request, *args, **kwargs)
        # We can't do this in the serializer because the serializer doesn't know about the user
        for patient in response.data:
            taggings = models.Tagging.objects.filter(patient_id=patient['id'])
            patient['tags'] = {t.tag_name: True for t in taggings if t.user is None or t.user == request.user}
        return response

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
        patient.set_tags(tags, request.user)

        serializer = serializers.PatientSerializer(patient)

        # We can't do this in the serializer because the serializer doesn't know about the user
        serializer.data['tags'] = tags

        return response.Response(serializer.data, status=status.HTTP_201_CREATED)

class PatientDetailView(LoginRequiredMixin, generics.RetrieveAPIView):
    model = models.Patient
    serializer_class = serializers.PatientSerializer

    def get(self, request, *args, **kwargs):
        response = super(PatientDetailView, self).get(request, *args, **kwargs)
        # We can't do this in the serializer because the serializer doesn't know about the user
        taggings = models.Tagging.objects.filter(patient_id=response.data['id'])
        response.data['tags'] = {t.tag_name: True for t in taggings if t.user is None or t.user == request.user}
        return response

class SingletonSubrecordDetail(LoginRequiredMixin, SingletonMixin, generics.RetrieveUpdateAPIView):
    def get_object(self, queryset=None):
        return getattr(self.patient, self.model.__name__.lower())

    def put(self, request, *args, **kwargs):
        response = super(SingletonSubrecordDetail, self).put(request, *args, **kwargs)
        if 'tags' in request.DATA:
            patient = models.Patient.objects.get(pk=request.DATA['patient'])
            patient.set_tags(request.DATA['tags'], request.user)
        return response

class SubrecordList(LoginRequiredMixin, SingletonMixin, generics.ListCreateAPIView):
    pass

class SubrecordDetail(LoginRequiredMixin, SingletonMixin, generics.RetrieveUpdateDestroyAPIView):
    def get_object(self, queryset=None):
        return getattr(self.patient, camelcase_to_underscore(self.model.__name__)).get(pk=self.kwargs['id'])

class PatientTemplateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(PatientTemplateView, self).get_context_data(**kwargs)
        context['tags'] = models.TAGS

        context['columns'] = []

        for column in schema.columns:
            column_context = {}
            name = camelcase_to_underscore(column.__name__)
            if isinstance(self, PatientListTemplateView) and name == 'microbiology_input':
                continue
            column_context['name'] = name
            column_context['title'] = getattr(column, '_title', name.replace('_', ' ').title())
            column_context['single'] = issubclass(column, models.SingletonSubrecord)
            column_context['template_path'] = name + '.html'
            column_context['modal_template_path'] = name + '_modal.html'
            context['columns'].append(column_context)

        return context

class PatientListTemplateView(PatientTemplateView):
    template_name = 'patient_list.html'

class PatientDetailTemplateView(PatientTemplateView):
    template_name = 'patient_detail.html'

class SearchTemplateView(PatientTemplateView):
    template_name = 'search.html'

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'opal.html'

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

    data = {'columns': columns}

    if request.GET.get('columns-only', 'no') == 'no':
        data['option_lists'] = {}
        data['synonyms'] = {}

        for name, model in option_models.items():
            option_list = []
            synonyms = {}
            for instance in model.objects.all():
                option_list.append(instance.name)
                for synonym in instance.synonyms.all():
                    option_list.append(synonym.name)
                    synonyms[synonym.name] = instance.name
            data['option_lists'][name] = option_list
            data['synonyms'][name] = synonyms

    return HttpResponse(json.dumps(data), mimetype='application/json')

class SearchResultsView(LoginRequiredMixin, views.APIView):
    renderer_classes = [renderers.JSONRenderer]

    def get(self, request, *args, **kwargs):
        GET = self.request.GET

        search_terms = {}
        filter_dict = {}

        if 'hospital_number' in GET:
            search_terms['hospital_number'] = GET['hospital_number']
            filter_dict['demographics__hospital_number__iexact'] = GET['hospital_number']

        if 'name' in GET:
            search_terms['name'] = GET['name']
            filter_dict['demographics__name__icontains'] = GET['name']

        if filter_dict:
            queryset = models.Patient.objects.filter(**filter_dict)
        else:
            queryset = models.Patient.objects.none()

        serializer = serializers.PatientSerializer(queryset, many=True)
        data = {'patients': serializer.data}

        # We cannot get the tags in the serializer because this requires the user
        for patient in data['patients']:
            taggings = models.Tagging.objects.filter(patient_id=patient['id'])
            patient['tags'] = {t.tag_name: True for t in taggings if t.user is None or t.user == request.user}

        data['search_terms'] = search_terms
        return response.Response(data)
