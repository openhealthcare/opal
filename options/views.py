import json
from django.http import HttpResponse
from options.models import Antimicrobial, Destination

def antimicrobials(request):
    data = [antimicrobial.name for antimicrobial in Antimicrobial.objects.all()]
    return HttpResponse(json.dumps(data), content_type="application/json")

def destinations(request):
    data = [destination.name for destination in Destination.objects.all()]
    return HttpResponse(json.dumps(data), content_type="application/json")
