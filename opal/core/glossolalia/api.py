from rest_framework import viewsets
from rest_framework.response import Response
from models import GlossolaliaSubscription
from opal.core.api import OPALRouter

router = OPALRouter()

class GlossolaliaViewSet(viewsets.ViewSet):
    base_name = 'glossolalia'

    def list(self, *args, **kwargs):
        queryset = GlossolaliaSubscription.objects.all()
        serialised = queryset.values(*GlossolaliaSubscription.SERIALISED_FIELDS)
        return Response(serialised)

    def update(self, request, pk=None): pass


router.register('glossolalia', GlossolaliaViewSet)
