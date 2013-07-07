import json
from django.db import IntegrityError
from django.core import serializers
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.http import require_http_methods
from rest_framework.utils.encoders import JSONEncoder
from records import models, exceptions

@require_http_methods(["POST"])
def patient_create(request):
    data = _get_request_data(request)
    patient = models.Patient.objects.create(**data)
    return _build_json_response(patient.serialize(), 201)

@require_http_methods(["GET"])
def patient_detail(request, id):
    try:
        patient = models.Admission.objects.get(pk=id)
    except models.Admission.DoesNotExist:
        return HttpResponseNotFound()
    return _build_json_response(patient.serialize(), 200)

@require_http_methods(["POST"])
def admission_create(request):
    data = _get_request_data(request)
    admission = models.Admission.objects.create(**data)
    return _build_json_response(admission.serialize(), 201)

@require_http_methods(["GET"])
def admission_detail(request, id):
    try:
        admission = models.Admission.objects.get(pk=id)
    except models.Admission.DoesNotExist:
        return HttpResponseNotFound()
    return _build_json_response(admission.serialize(), 200)

@require_http_methods(["POST"])
def subrecord_create(request, subrecord_name):
    model = models.get_subrecord_model(subrecord_name)
    data = _get_request_data(request)
    try:
        subrecord = model.objects.create(**data)
        return _build_json_response(subrecord.serialize(), 201)
    except (IntegrityError, ValidationError) as e:
        return _build_json_response(e.args, 400)


@require_http_methods(["GET", "PUT"])
def subrecord_detail(request, subrecord_name, id):
    model = models.get_subrecord_model(subrecord_name)
    if model is None:
        return HttpResponseNotFound()
    else:
        try:
            subrecord = model.objects.get(pk=id)
        except model.DoesNotExist:
            return HttpResponseNotFound()

    if request.method == 'GET':
        return _get_subcrecord(subrecord)
    elif request.method == 'PUT':
        return _update_subrecord(subrecord, _get_request_data(request))

def _get_request_data(request):
    data = request.read()
    return json.loads(data)

def _build_json_response(data, status_code=200):
    response = HttpResponse()
    response['Content-Type'] = 'application/json'
    response.content = json.dumps(data, cls=JSONEncoder)
    response.status_code = status_code
    return response

def _get_subcrecord(subrecord):
    return _build_json_response(subrecord.serialize())

def _update_subrecord(subrecord, data):
    try:
        subrecord.update(data)
        return _build_json_response(subrecord.serialize())
    except exceptions.APIError as e:
        return _build_json_response(e.args, 400)
    except exceptions.ConsistencyError as e:
        return _build_json_response(e.args, 409)
