import json
from django.http import HttpResponse
from options.models import option_models

def options_view(request, model_name):
    model = option_models[model_name]
    data = []
    for instance in model.objects.all():
        data.append([instance.name, instance.name])
        for synonym in instance.synonyms.all():
            data.append([synonym.name, instance.name])
    return HttpResponse(json.dumps(data), content_type="application/json")
