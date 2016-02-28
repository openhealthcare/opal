from rest_framework import viewsets
from rest_framework.response import Response

from opal.core.subrecords import subrecords
from opal.core.api import router
from opal.core.views import _get_request_data, _build_json_response
from opal.utils import camelcase_to_underscore

from opal.core.glossolalia.models import GlossolaliaSubscription

# class GlossolaliaViewSet(viewsets.ViewSet):
#     base_name = 'glossolalia'

#     def list(self, *args, **kwargs):
#         queryset = GlossolaliaSubscription.objects.all()
#         serialised = queryset.values(*GlossolaliaSubscription.SERIALISED_FIELDS)
#         return Response(serialised)

#     def update(self, request, pk=None): pass

class GlossSubrecordViewSet(viewsets.ViewSet):
    base_name = 'glosssubrecord'

    def create(self, request):
        identifier = request.data['identifier']
        data = request.data['data']
        self.model.create_or_update_from_gloss(identifier, data)
        return _build_json_response('Hai')

#router.register('glossolalia', GlossolaliaViewSet)
for sub in subrecords():
    sub_name = camelcase_to_underscore(sub.__name__)

    class SubViewSet(GlossSubrecordViewSet):
        base_name = 'gloss' + sub_name
        model = sub

    router.register('gloss' + sub_name, SubViewSet)
