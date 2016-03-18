import requests
from rest_framework import viewsets
from rest_framework.response import Response
from models import GlossolaliaSubscription
from opal.core.api import OPALRouter
from django.conf import settings

router = OPALRouter()

class GlossolaliaViewSet(viewsets.ViewSet):
    base_name = 'glossolalia'

    def list(self, *args, **kwargs):
        queryset = GlossolaliaSubscription.objects.all()
        serialised = queryset.values(*GlossolaliaSubscription.SERIALISED_FIELDS)
        return Response(serialised)

    def update(self, request, pk=None): pass


router.register('glossolalia', GlossolaliaViewSet)


class SubscriptionApi(object):
    def subscribe_url(self, hospital_number):
        return settings.GLOSSOLALIA_URL + "/subscribe/uclh/" + hospital_number

    def unsubscribe_url(self, hospital_number):
        return settings.GLOSSOLALIA_URL + "/unsubscribe/uclh/" + hospital_number

    def send_upstream(self, url, data=None):
        # handle all key logic and response validation
        return requests.post(url, data=data)

    def subscribe_to_gloss(self, hospital_number):
        self.send_upstream(self.subscribe_url(hospital_number))

    def unsubscribe_to_gloss(self, hospital_number):
        self.send_upstream(self.unsubscribe_url(hospital_number))
