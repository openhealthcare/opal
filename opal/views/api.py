"""
Public facing API views
"""
import collections

from django.conf import settings
from django.views.generic import View
from rest_framework import routers, viewsets
from rest_framework.decorators import list_route
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

from opal import application, schemas
from opal.utils import stringport
from opal.utils.views import _get_request_data, _build_json_response

app = application.get_app()

# TODO This is stupid - we can fully deprecate this please?
try:
    options = stringport(settings.OPAL_OPTIONS_MODULE)
    micro_test_defaults = options.micro_test_defaults
except AttributeError:
    class options:
        model_names = []
    micro_test_defaults = []


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


class OptionsViewSet(viewsets.ViewSet):
    """
    Returns various metadata concerning this OPAL instance: 
    Lookuplists, micro test defaults, tag hierarchy, macros.
    """
    base_name = 'options'
    
    def list(self, request):
        from opal.utils.models import LookupList
        from opal.models import Synonym, Team, Macro
        
        data = {}
        for model in LookupList.__subclasses__():
            options = [instance.name for instance in model.objects.all()]
            data[model.__name__.lower()] = options

        for synonym in Synonym.objects.all():
            try:
                co =  synonym.content_object
            except AttributeError:
                continue
            name = type(co).__name__.lower()
            data[name].append(synonym.name)

        for name in data:
            data[name].sort()

        data['micro_test_defaults'] = micro_test_defaults

        tag_hierarchy = collections.defaultdict(list)
        tag_display = {}

        if request.user.is_authenticated():
            teams = Team.for_user(request.user)
            for team in teams:
                if team.parent:
                    continue # Will be filled in at the appropriate point! 
                tag_display[team.name] = team.title

                subteams = [st for st in teams if st.parent == team]
                tag_hierarchy[team.name] = [st.name for st in subteams]
                for sub in subteams: 
                    tag_display[sub.name] = sub.title

        data['tag_hierarchy'] = tag_hierarchy
        data['tag_display'] = tag_display

        data['macros'] = Macro.to_dict()

        return _build_json_response(data)
        

router.register('flow', FlowViewSet)
router.register('record', RecordViewSet)
router.register('list-schema', ListSchemaViewSet)
router.register('extract-schema', ExtractSchemaViewSet)
router.register('options', OptionsViewSet)


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
