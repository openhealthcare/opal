from rest_framework import routers, status, viewsets
from rest_framework.response import Response
from models import GlossolaliaSubscription
from opal.core.api import OPALRouter

router = OPALRouter()

class GlossolaliaViewSet(viewsets.ViewSet):
    base_name = 'glossolalia'

    def list(self, request):
        queryset = GlossolaliaSubscription.objects.all().values(*SERIALISED_FIELDS)
        serialised = queryset.values(*SERIALISED_FIELDS)
        return Response(serialised)

    def update(self, request, pk=None):
        pass

router.register('glossolalia', GlossolaliaViewSet)
