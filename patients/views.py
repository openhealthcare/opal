import json
import datetime
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.template.loader import select_template
from django.utils.decorators import method_decorator
from django.utils import formats
from django.contrib.auth.decorators import login_required
from utils import camelcase_to_underscore
from patients import models, schema
from options.models import option_models, Synonym

class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)

def patient_detail_view(request, pk):
    try:
        patient = models.Patient.objects.get(pk=pk)
    except models.Patient.DoesNotExist:
        return HttpResponseNotFound

    return _build_json_response(patient.to_dict(), 200)

def patient_list_and_create_view(request):
    if request.method == 'GET':
        GET = request.GET

        search_terms = {}
        filter_dict = {}

        if 'hospital_number' in GET:
            search_terms['hospital_number'] = GET['hospital_number']
            filter_dict['demographics__hospital_number__iexact'] = GET['hospital_number']

        if 'name' in GET:
            search_terms['name'] = GET['name']
            filter_dict['demographics__name__icontains'] = GET['name']

        if filter_dict:
            patients = models.Patient.objects.filter(**filter_dict)
        else:
            patients = models.Patient.objects.all()

        return _build_json_response([patient.to_dict() for patient in patients])

    elif request.method == 'POST':
        patient = models.Patient.objects.create()
        data = _get_request_data(request)
        patient.update_from_dict(data, request.user)
        return _build_json_response(patient.to_dict(), 201)

def subrecord_detail_view(request, model, pk):
    try:
        subrecord = model.objects.get(pk=pk)
    except model.DoesNotExist:
        return HttpResponseNotFound

    if request.method == 'PUT':
        data = _get_request_data(request)
        subrecord.update_from_dict(data, request.user)

    return _build_json_response(subrecord.to_dict())

def subrecord_create_view(request, model):
    subrecord = model()
    data = _get_request_data(request)
    subrecord.update_from_dict(data, request.user)
    return _build_json_response(subrecord.to_dict(), 201)

def _get_request_data(request):
    data = request.read()
    return json.loads(data)

def _build_json_response(data, status_code=200):
    response = HttpResponse()
    response['Content-Type'] = 'application/json'
    response.content = json.dumps(data, cls=DjangoJSONEncoder)
    response.status_code = status_code
    return response


class PatientTemplateView(TemplateView):

    column_schema = schema.columns

    def get_column_context(self):
        """
        Return the context for our columns
        """
        context = []
        for column in self.column_schema:
            column_context = {}
            name = camelcase_to_underscore(column.__name__)
            if isinstance(self, PatientListTemplateView) and name == 'microbiology_input':
                continue
            column_context['name'] = name
            column_context['title'] = getattr(column, '_title',
                                              name.replace('_', ' ').title())
            column_context['single'] = column._is_singleton
            column_context['template_path'] = name + '.html'
            column_context['modal_template_path'] = name + '_modal.html'
            column_context['detail_template_path'] = select_template([name + '_detail.html', name + '.html']).name
            context.append(column_context)
        return context

    def get_context_data(self, **kwargs):
        context = super(PatientTemplateView, self).get_context_data(**kwargs)
        context['tags'] = models.TAGS
        context['columns'] = self.get_column_context()
        return context


class PatientListTemplateView(PatientTemplateView):
    template_name = 'patient_list.html'

class PatientDetailTemplateView(PatientTemplateView):
    template_name = 'patient_detail.html'
    column_schema = schema.detail_columns

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
            'name': column.get_api_name(),
            'single': column._is_singleton,
            'fields': column.build_field_schema()
        })

    return _build_json_response(columns)
