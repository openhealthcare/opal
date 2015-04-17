"""
Public facing API views
"""
from django.views.generic import View

from rest_framework import routers, viewsets
from rest_framework.decorators import list_route

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

from opal import application, schemas
from opal.utils.views import _get_request_data, _build_json_response

app = application.get_app()

class OPALRouter(routers.DefaultRouter):
    def get_default_base_name(self, viewset):
        name = getattr(viewset, 'base_name', None)
        if name is None:
            return super(OPALRouter, self).get_default_base_name(viewset)
        return name

router = OPALRouter()

class FlowViewSet(viewsets.ViewSet):
    """
    Return the Flow routes for this application.
    
    For more detail on OPAL Flows, see the documentation 
    """
    base_name = 'flow'

    def list(self, request):
        flows = app.flows()
        return Response(flows)


class RecordViewSet(viewsets.ViewSet):
    """
    Return the serialization of all active record types ready to
    initialize on the client side.
    """
    base_name = 'record'

    def list(self, request):
        return Response(schemas.list_records())

    
class ListSchemaViewSet(viewsets.ViewSet):
    """
    Returns the schema for our active lists
    """
    base_name = 'list-schema'

    def list(self, request):
        return Response(schemas.list_schemas())

    
class ExtractSchemaViewSet(viewsets.ViewSet):
    """
    Returns the schema to build our extract query builder
    """
    base_name = 'extract-schema'
    
    def list(self, request):
        return Response(schemas.extract_schema())


router.register('flow', FlowViewSet)
router.register('record', RecordViewSet)
router.register('list-schema', ListSchemaViewSet)
router.register('extract-schema', ExtractSchemaViewSet)


class APIAdmitEpisodeView(View):
    """
    Admit an episode from upstream!
    """
    def post(self, *args, **kwargs):
        data = _get_request_data(self.request)
        print data
        resp = {'ok': 'Got your admission just fine - thanks!'}
        return _build_json_response(resp)


class APIReferPatientView(View):
    """
    Refer a particular episode of care to a new team
    """
    def post(self, *args, **kwargs):
        """
        Expects PATIENT, EPISODE, TARGET
        """
        from opal.models import Episode
        data = _get_request_data(self.request)
        episode = Episode.objects.get(pk=data['episode'])
        current_tags = episode.get_tag_names(None)
        if not data['target'] in current_tags:
            print "Setting", data['target']
            current_tags.append(data['target'])
            episode.set_tag_names(current_tags, None)
        resp = {'ok': 'Got your referral just fine - thanks!'}
        return _build_json_response(resp)

    
class APISubrecordDetailView(View):
    """
    Main API entrypoint for Subrecords. 
    """

    def dispatch(self, *args, **kwargs):
        """
        Try to find our subrecord if we're not POSTING?

        404 Appropriately.        
        """

    def get(self, *args, **kwargs):
        """
        Just render the JSON for this subrecord!
        """
        return

    def post(self, *args, **kwargs):
        """
        Create a subrecord
        """
        return

    def put(self, *args, **kwargs):
        """
        Update a subrecord
        """
        return

    def delete(self, *args, **kwargs):
        """
        Delete a subrecord
        """
