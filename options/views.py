import json
from django.http import HttpResponse
from options.models import option_models

def options_view(request, model_name):
    model = option_models[model_name]
    data = [instance.name for instance in model.objects.all()]
    return HttpResponse(json.dumps(data), content_type="application/json")
