"""
Public facing API views
"""
from django.conf import settings
from django.views.generic import View
from django.contrib.contenttypes.models import ContentType
from rest_framework import routers, status, viewsets
from rest_framework.response import Response

from opal.models import (
    Episode, Synonym, Patient, PatientRecordAccess, PatientSubrecord
)
from opal.core import application, exceptions, metadata, plugins, schemas
from opal.core.lookuplists import LookupList
from opal.utils import stringport, camelcase_to_underscore
from opal.core.subrecords import subrecords
from opal.core.views import _get_request_data, _build_json_response
from opal.core.patient_lists import (
    PatientList, TaggedPatientListMetadata, FirstListMetadata
)

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
        try:
            return fn(self, request, Episode.objects.get(pk=pk))
        except Episode.DoesNotExist:
            return Response({'error': 'Episode does not exist'}, status=status.HTTP_404_NOT_FOUND)
    return get_item


class RecordViewSet(viewsets.ViewSet):
    """
    Return the serialization of all active record types ready to
    initialize on the client side.
    """
    base_name = 'record'

    def list(self, request):
        return Response(schemas.list_records())


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
            data[model.get_api_name()] = options

        model_to_ct = ContentType.objects.get_for_models(
            *subclasses
        )

        for model, ct in model_to_ct.iteritems():
            synonyms = Synonym.objects.filter(content_type=ct).values_list(
                "name", flat=True
            )
            data[model.get_api_name()].extend(synonyms)

        for name in data:
            data[name].sort()

        data.update(metadata.MicroTestDefaultsMetadata.to_dict())
        data.update(metadata.MacrosMetadata.to_dict())
        data.update(TaggedPatientListMetadata.to_dict(user=request.user))
        data.update(FirstListMetadata.to_dict(user=request.user))
        return Response(data)


class ReferenceDataViewSet(viewsets.ViewSet):
    """
    API for referencedata
    """
    base_name = 'referencedata'

    def list(self, request):
        data = {}
        subclasses = LookupList.__subclasses__()
        for model in subclasses:
            options = list(model.objects.all().values_list("name", flat=True))
            data[model.get_api_name()] = options

        model_to_ct = ContentType.objects.get_for_models(
            *subclasses
        )

        for model, ct in model_to_ct.iteritems():
            synonyms = Synonym.objects.filter(content_type=ct).values_list(
                "name", flat=True
            )
            data[model.get_api_name()].extend(synonyms)

        for name in data:
            data[name].sort()
        return Response(data)

    def retrieve(self, request, pk=None):
        the_list = None
        for lookuplist in LookupList.__subclasses__():
            if lookuplist.get_api_name() == pk:
                the_list = lookuplist
                break
        if the_list:
            values = list(the_list.objects.all().values_list('name', flat=True))
            ct = ContentType.objects.get_for_model(the_list)
            synonyms = Synonym.objects.filter(content_type=ct).values_list(
                'name', flat=True
            )
            values += list(synonyms)
            return Response(values)

        return Response({'error': 'Item does not exist'}, status=status.HTTP_404_NOT_FOUND)


class MetadataViewSet(viewsets.ViewSet):
    """
    Our metadata API
    """
    base_name = 'metadata'

    def list(self, request):
        data = {}
        for meta in metadata.Metadata.list():
            data.update(meta.to_dict(user=request.user))
        return Response(data)

    def retrieve(self, request, pk=None):
        try:
            meta = metadata.Metadata.get(pk)
            return Response(meta.to_dict(user=request.user))
        except ValueError:
            return Response({'error': 'Metadata does not exist'}, status=status.HTTP_404_NOT_FOUND)


class SubrecordViewSet(viewsets.ViewSet):
    """
    This is the base viewset for our subrecords.
    """

    def create(self, request):
        """
        * Create a subrecord
        * Ping our integration upstream interface
        * Render the created subrecord back to the requester

        Raise appropriate errors for:

        * Nonexistant episode
        * Unexpected fields being passed in
        """
        subrecord = self.model()
        try:
            episode = Episode.objects.get(pk=request.data['episode_id'])
        except Episode.DoesNotExist:
            return Response('Nonexistant episode', status=status.HTTP_400_BAD_REQUEST)

        if isinstance(subrecord, PatientSubrecord):
            del request.data['episode_id']
            patient_id = episode.patient.pk
            request.data['patient_id'] = patient_id

        subrecord.update_from_dict(request.data, request.user)
        episode = Episode.objects.get(pk=episode.pk)

        return _build_json_response(
            subrecord.to_dict(request.user),
            status_code=status.HTTP_201_CREATED
        )

    @item_from_pk
    def retrieve(self, request, item):
        return Response(item.to_dict(request.user))

    @item_from_pk
    def update(self, request, item):
        try:
            item.update_from_dict(request.data, request.user)
        except exceptions.APIError:
            return Response({'error': 'Unexpected field name'},
                            status=status.HTTP_400_BAD_REQUEST)
        except exceptions.ConsistencyError:
            return Response({'error': 'Item has changed'}, status=status.HTTP_409_CONFLICT)
        return _build_json_response(
            item.to_dict(request.user),
            status_code=status.HTTP_202_ACCEPTED
        )

    @item_from_pk
    def destroy(self, request, item):
        item.delete()
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
    Returns taggings associated with episodes
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
        episode.set_tag_names(tag_names, request.user)
        return Response(episode.tagging_dict(request.user)[0], status=status.HTTP_202_ACCEPTED)


class EpisodeViewSet(viewsets.ViewSet):
    """
    Episodes of care
    """
    base_name = 'episode'

    def list(self, request):
        return _build_json_response([e.to_dict(request.user) for e in Episode.objects.all()])

    def create(self, request):
        """
        Create a new episode, optionally implicitly creating a patient.

        * Extract the data from the request
        * Create or locate the patient
        * Create a new episode
        * Update the patient with any extra data passed in
        * return the patient
        """
        demographics_data = request.data.pop('demographics', None)
        location_data     = request.data.pop('location', {})
        tagging           = request.data.pop('tagging', {})

        hospital_number = demographics_data.get('hospital_number', None)
        if hospital_number:
            patient, created = Patient.objects.get_or_create(
                demographics__hospital_number=hospital_number)
            if created:
                demographics = patient.demographics_set.get()
                demographics.hospital_number = hospital_number
                demographics.save()
        else:
            patient = Patient.objects.create()

        patient.update_from_demographics_dict(demographics_data, request.user)

        episode = Episode(patient=patient)
        episode.update_from_dict(request.data, request.user)
        location = episode.location_set.get()
        location.update_from_dict(location_data, request.user)
        episode.set_tag_names([n for n, v in tagging[0].items() if v], request.user)
        serialised = episode.to_dict(request.user)

        return _build_json_response(serialised, status_code=status.HTTP_201_CREATED)

    @episode_from_pk
    def update(self, request, episode):
        try:
            episode.update_from_dict(request.data, request.user)
            return _build_json_response(episode.to_dict(request.user, shallow=True))
        except exceptions.ConsistencyError:
            return _build_json_response({'error': 'Item has changed'}, 409)

    @episode_from_pk
    def retrieve(self, request, episode):
        return _build_json_response(episode.to_dict(request.user))


class PatientViewSet(viewsets.ViewSet):
    base_name = 'patient'

    def retrieve(self, request, pk=None):
        patient = Patient.objects.get(pk=pk)
        PatientRecordAccess.objects.create(patient=patient, user=request.user)
        return _build_json_response(patient.to_dict(request.user))


class PatientRecordAccessViewSet(viewsets.ViewSet):
    base_name = 'patientrecordaccess'

    def retrieve(self, request, pk=None):
        return _build_json_response([
            a.to_dict(request.user) for a in PatientRecordAccess.objects.filter(patient_id=pk)
        ])

class PatientListViewSet(viewsets.ViewSet):
    base_name = 'patientlist'

    def retrieve(self, request, pk=None):
        try:
            patientlist = PatientList.get(pk)()
        except ValueError:
            return Response({'error': 'List does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return _build_json_response(patientlist.to_dict(request.user))


router.register('patient', PatientViewSet)
router.register('episode', EpisodeViewSet)
router.register('record', RecordViewSet)
router.register('extract-schema', ExtractSchemaViewSet)
router.register('userprofile', UserProfileViewSet)
router.register('tagging', TaggingViewSet)
router.register('patientlist', PatientListViewSet)
router.register('patientrecordaccess', PatientRecordAccessViewSet)

router.register('options', OptionsViewSet)
router.register('referencedata', ReferenceDataViewSet)
router.register('metadata', MetadataViewSet)

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
    Refer a patient
    """
    # TODO - explore when this is used - seems like there should be a better way?
    def post(self, *args, **kwargs):
        """
        Expects PATIENT, EPISODE, TARGET
        """
        data = _get_request_data(self.request)
        episode = Episode.objects.get(pk=data['episode'])
        current_tags = episode.get_tag_names(None)
        if not data['target'] in current_tags:
            current_tags.append(data['target'])
            episode.set_tag_names(current_tags, None)
        resp = {'ok': 'Got your referral just fine - thanks!'}
        return _build_json_response(resp)


class EpisodeListApi(View):
    """
    Return serialised subsets of active episodes by tag.
    """
    def get(self, *args, **kwargs):
        # while we manage transition lets allow a fall back to the old way
        name = kwargs['tag']
        if 'subtag' in kwargs:
            name += '-' + kwargs['subtag']
        patient_list = PatientList.get(name)()
        return _build_json_response(patient_list.to_dict(self.request.user))
