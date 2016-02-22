"""
Public facing API views
"""
import collections

from django.conf import settings
from django.views.generic import View
from django.contrib.contenttypes.models import ContentType
from rest_framework import routers, status, viewsets
from rest_framework.response import Response
from opal.models import Episode, Synonym, Team, Macro
from opal.core import application, exceptions, plugins
from opal.core import glossolalia
from opal.core.lookuplists import LookupList
from opal.utils import stringport, camelcase_to_underscore
from opal.core import schemas
from opal.core.subrecords import subrecords
from opal.core.views import _get_request_data, _build_json_response

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
            return routers.DefaultRouter.get_default_base_name(self, viewset)
        return name

router = OPALRouter()

def item_from_pk(fn):
    """
    Decorator that passes an instance or returns a 404 from pk kwarg.
    """
    def get_item(self, request, pk=None):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Item does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return fn(self, request, item)
    return get_item

def episode_from_pk(fn):
    """
    Decorator that passes an episode or returns a 404 from pk kwarg.
    """
    def get_item(self, request, pk=None):
        from opal.models import Episode
        try:
            return fn(self, request, Episode.objects.get(pk=pk))
        except Episode.DoesNotExist:
            return Response({'error': 'Episode does not exist'}, status=status.HTTP_404_NOT_FOUND)
    return get_item

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


# TODO:
# Deprecate this fully
class OptionsViewSet(viewsets.ViewSet):
    """
    Returns various metadata concerning this OPAL instance:
    Lookuplists, micro test defaults, tag hierarchy, macros.
    """
    base_name = 'options'

    def list(self, request):


        data = {}
        subclasses = LookupList.__subclasses__()
        for model in subclasses:
            options = list(model.objects.all().values_list("name", flat=True))
            data[model.__name__.lower()] = options

        model_to_ct = ContentType.objects.get_for_models(
            *subclasses
        )

        for model, ct in model_to_ct.iteritems():
            synonyms = Synonym.objects.filter(content_type=ct).values_list(
                "name", flat=True
            )
            data[model.__name__.lower()].extend(synonyms)

        for name in data:
            data[name].sort()

        data['micro_test_defaults'] = micro_test_defaults

        tag_hierarchy = collections.defaultdict(list)
        tag_visible_in_list = []
        tag_display = {}

        if request.user.is_authenticated():
            teams = Team.for_user(request.user)
            for team in teams:
                if team.parent:
                    continue # Will be filled in at the appropriate point!
                tag_display[team.name] = team.title

                if team.visible_in_list:
                    tag_visible_in_list.append(team.name)

                subteams = [st for st in teams if st.parent == team]
                tag_hierarchy[team.name] = [st.name for st in subteams]
                for sub in subteams:
                    tag_display[sub.name] = sub.title

                    if sub.visible_in_list:
                        tag_visible_in_list.append(sub.name)

        data['tag_hierarchy'] = tag_hierarchy
        data['tag_display'] = tag_display
        data['tag_visible_in_list'] = tag_visible_in_list
        data['macros'] = Macro.to_dict()

        return Response(data)


class SubrecordViewSet(viewsets.ViewSet):
    """
    This is the base viewset for our subrecords.
    """

    def _item_to_dict(self, item, user):
        """
        Given an item, serialize either the patient or episode it is a
        subrecord of.
        """
        try:
            return item.episode.to_dict(user)
        except AttributeError:
            return item.patient.to_dict(user)

    def create(self, request):
        """
        * Create a subrecord
        * Ping our integration upstream interface
        * Render the created subrecord back to the requester

        Raise appropriate errors for:

        * Nonexistant episode
        * Unexpected fields being passed in
        """
        from opal.models import Episode, PatientSubrecord

        subrecord = self.model()
        try:
            episode = Episode.objects.get(pk=request.data['episode_id'])
        except Episode.DoesNotExist:
            return Response('Nonexistant episode', status=status.HTTP_400_BAD_REQUEST)
        pre = episode.to_dict(request.user)

        if isinstance(subrecord, PatientSubrecord):
            del request.data['episode_id']
            patient_id = episode.patient.pk
            request.data['patient_id'] = patient_id

        try:
            subrecord.update_from_dict(request.data, request.user)
        except exceptions.APIError:
            return Response({'error': 'Unexpected field name'}, status=status.HTTP_400_BAD_REQUEST)

        episode = Episode.objects.get(pk=episode.pk)
        post = episode.to_dict(request.user)
        glossolalia.change(pre, post)

        return Response(subrecord.to_dict(request.user), status=status.HTTP_201_CREATED)

    @item_from_pk
    def retrieve(self, request, item):
        return Response(item.to_dict(request.user))

    @item_from_pk
    def update(self, request, item):
        pre = self._item_to_dict(item, request.user)
        try:
            item.update_from_dict(request.data, request.user)
        except exceptions.APIError:
            return Response({'error': 'Unexpected field name'},
                            status=status.HTTP_400_BAD_REQUEST)
        except exceptions.ConsistencyError:
            return Response({'error': 'Item has changed'}, status=status.HTTP_409_CONFLICT)
        glossolalia.change(pre, self._item_to_dict(item, request.user))
        return Response(item.to_dict(request.user), status=status.HTTP_202_ACCEPTED)

    @item_from_pk
    def destroy(self, request, item):
        pre = self._item_to_dict(item, request.user)
        item.delete()
        glossolalia.change(pre, self._item_to_dict(item, request.user))
        return Response('deleted', status=status.HTTP_202_ACCEPTED)


class UserProfileViewSet(viewsets.ViewSet):
    """
    Returns the user profile details for the currently logged in user
    """
    base_name = 'userprofile'

    def list(self, request):
        if not request.user.is_authenticated():
            return Response(
                {'error': 'Only valid for authenticated users'},
                status=status.HTTP_401_UNAUTHORIZED)
        profile = request.user.profile
        return Response(profile.to_dict())


class TaggingViewSet(viewsets.ViewSet):
    """
    Associating episodes with teams
    """
    base_name = 'tagging'

    @episode_from_pk
    def retrieve(self, request, episode):
        return Response(episode.tagging_dict(request.user)[0], status=status.HTTP_200_OK)

    @episode_from_pk
    def update(self, request, episode):
        if 'id' in request.data:
            del request.data['id']
        tag_names = [n for n, v in request.data.items() if v]
        pre = episode.to_dict(request.user)
        episode.set_tag_names(tag_names, request.user)
        post = episode.to_dict(request.user)
        glossolalia.transfer(pre, post)
        return Response(episode.tagging_dict(request.user)[0], status=status.HTTP_202_ACCEPTED)


class EpisodeViewSet(viewsets.ViewSet):
    """
    Episodes of care
    """
    base_name = 'episode'

    def list(self, request):
        from opal.models import Episode

        tag    = request.query_params.get('tag', None)
        subtag = request.query_params.get('subtag', None)

        filter_kwargs = {'tagging__archived': False}
        if subtag:
            filter_kwargs['tagging__team__name'] = subtag
        elif tag:
            filter_kwargs['tagging__team__name'] = tag

        if tag == 'mine':
            filter_kwargs['tagging__user'] = request.user

        if not (subtag or tag):
            return Response([e.to_dict(request.user) for e in Episode.objects.all()])

        serialised = Episode.objects.serialised_active(
            request.user, **filter_kwargs)

        return Response(serialised)

    def create(self, request):
        from opal.models import Patient

        hospital_number = request.data.pop('patient_hospital_number', None)
        tagging = request.data.pop('tagging', {})
        if hospital_number:
            patient, created = Patient.objects.get_or_create(
                demographics__hospital_number=hospital_number)
            if created:
                demographics = patient.demographics_set.get()
                demographics.hospital_number = hospital_number
                demographics.save()
        else:
            patient = Patient.objects.create()

        episode = Episode(patient=patient)
        episode.update_from_dict(request.data, request.user)
        episode.set_tag_names([n for n, v in tagging[0].items() if v], request.user)
        serialised = episode.to_dict(request.user)
        return Response(serialised, status=status.HTTP_201_CREATED)

    @episode_from_pk
    def retrieve(self, request, episode):
        return Response(episode.to_dict(request.user))


class PatientViewSet(viewsets.ViewSet):
    base_name = 'patient'

    def list(self, request):
        from opal.models import Patient

        return Response([p.to_dict(request.user) for p in Patient.objects.all()])

    def retrieve(self, request, pk=None):
        from opal.models import Patient

        patient = Patient.objects.get(pk=pk)
        return Response(patient.to_dict(request.user))


router.register('patient', PatientViewSet)
router.register('episode', EpisodeViewSet)
router.register('flow', FlowViewSet)
router.register('record', RecordViewSet)
router.register('list-schema', ListSchemaViewSet)
router.register('extract-schema', ExtractSchemaViewSet)
router.register('options', OptionsViewSet)
router.register('userprofile', UserProfileViewSet)
router.register('tagging', TaggingViewSet)

for subrecord in subrecords():
    sub_name = camelcase_to_underscore(subrecord.__name__)
    class SubViewSet(SubrecordViewSet):
        base_name = sub_name
        model     = subrecord

    router.register(sub_name, SubViewSet)

for plugin in plugins.plugins():
    for api in plugin.apis:
        router.register(*api)


class APIAdmitEpisodeView(View):
    """
    Admit an episode from upstream!
    """
    def post(self, *args, **kwargs):
        data = _get_request_data(self.request)
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
            current_tags.append(data['target'])
            episode.set_tag_names(current_tags, None)
        resp = {'ok': 'Got your referral just fine - thanks!'}
        return _build_json_response(resp)
