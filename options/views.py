import json
from django.http import HttpResponse
from options.models import Destination

def destinations(request):
    data = [destination.name for destination in Destination.objects.all()]
    return HttpResponse(json.dumps(data), content_type="application/json")
