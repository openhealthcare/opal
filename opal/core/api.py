"""
Public facing API views
"""
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from rest_framework import routers, status, viewsets
from rest_framework.permissions import IsAuthenticated

from opal.models import (
    Episode, Synonym, Patient, PatientRecordAccess, PatientSubrecord
)
from opal.core import application, exceptions, metadata, plugins, schemas
from opal.core.lookuplists import LookupList
from opal.utils import camelcase_to_underscore
from opal.core.subrecords import subrecords
from opal.core.views import json_response
from opal.core.patient_lists import PatientList


app = application.get_app()


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
            return json_response(
                {'error': 'Item does not exist'},
                status_code=status.HTTP_404_NOT_FOUND
            )
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
            return json_response(
                {'error': 'Episode does not exist'},
                status_code=status.HTTP_404_NOT_FOUND
            )
    return get_item


def patient_from_pk(fn):
    """
    Decorator that passes an episode or returns a 404 from pk kwarg.
    """
    def get_item(self, request, pk=None):
        item = get_object_or_404(Patient.objects.all(), pk=pk)
        return fn(self, request, item)
    return get_item


class LoginRequiredViewset(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)


class RecordViewSet(LoginRequiredViewset):
    """
    Return the serialization of all active record types ready to
    initialize on the client side.
    """
    base_name = 'record'

    def list(self, request):
        return json_response(schemas.list_records())


class ExtractSchemaViewSet(LoginRequiredViewset):
    """
    Returns the schema to build our extract query builder
    """
    base_name = 'extract-schema'

    def list(self, request):
        return json_response(schemas.extract_schema())


class ReferenceDataViewSet(LoginRequiredViewset):
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

        for model, ct in model_to_ct.items():
            synonyms = Synonym.objects.filter(content_type=ct).values_list(
                "name", flat=True
            )
            data[model.get_api_name()].extend(synonyms)

        for name in data:
            data[name].sort()
        return json_response(data)

    def retrieve(self, request, pk=None):
        the_list = None
        for lookuplist in LookupList.__subclasses__():
            if lookuplist.get_api_name() == pk:
                the_list = lookuplist
                break
        if the_list:
            values = list(
                the_list.objects.all().values_list('name', flat=True)
            )
            ct = ContentType.objects.get_for_model(the_list)
            synonyms = Synonym.objects.filter(content_type=ct).values_list(
                'name', flat=True
            )
            values += list(synonyms)
            return json_response(values)

        return json_response(
            {'error': 'Item does not exist'},
            status_code=status.HTTP_404_NOT_FOUND
        )


class MetadataViewSet(LoginRequiredViewset):
    """
    Our metadata API
    """
    base_name = 'metadata'

    def list(self, request):
        data = {}
        for meta in metadata.Metadata.list():
            data.update(meta.to_dict(user=request.user))
        return json_response(data)

    def retrieve(self, request, pk=None):
        try:
            meta = metadata.Metadata.get(pk)
            return json_response(meta.to_dict(user=request.user))
        except ValueError:
            return json_response(
                {'error': 'Metadata does not exist'},
                status_code=status.HTTP_404_NOT_FOUND
            )


class SubrecordViewSet(LoginRequiredViewset):
    """
    This is the base viewset for our subrecords.
    """

    def list(self, request):
        """
        Return all instances of this subrecord as a list.
        """
        queryset = self.model.objects.all()
        return json_response([s.to_dict(request.user) for s in queryset])

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
            return json_response(
                'Nonexistant episode', status_code=status.HTTP_400_BAD_REQUEST
            )

        if isinstance(subrecord, PatientSubrecord):
            del request.data['episode_id']
            patient_id = episode.patient.pk
            request.data['patient_id'] = patient_id

        subrecord.update_from_dict(request.data, request.user)
        episode = Episode.objects.get(pk=episode.pk)

        return json_response(
            subrecord.to_dict(request.user),
            status_code=status.HTTP_201_CREATED
        )

    @item_from_pk
    def retrieve(self, request, item):
        return json_response(item.to_dict(request.user))

    @item_from_pk
    def update(self, request, item):
        try:
            item.update_from_dict(request.data, request.user)
        except exceptions.APIError:
            return json_response({'error': 'Unexpected field name'},
                                 status_code=status.HTTP_400_BAD_REQUEST)
        except exceptions.ConsistencyError:
            return json_response(
                {'error': 'Item has changed'},
                status_code=status.HTTP_409_CONFLICT
            )
        return json_response(
            item.to_dict(request.user),
            status_code=status.HTTP_202_ACCEPTED
        )

    @item_from_pk
    def destroy(self, request, item):
        item.delete()
        return json_response('deleted', status_code=status.HTTP_202_ACCEPTED)


class UserProfileViewSet(LoginRequiredViewset):
    """
    Returns the user profile details for the currently logged in user
    """
    base_name = 'userprofile'

    def list(self, request):
        profile = request.user.profile
        return json_response(profile.to_dict())


class TaggingViewSet(LoginRequiredViewset):
    """
    Returns taggings associated with episodes
    """
    base_name = 'tagging'

    @episode_from_pk
    def retrieve(self, request, episode):
        return json_response(
            episode.tagging_dict(request.user)[0],
            status_code=status.HTTP_200_OK
        )

    @episode_from_pk
    def update(self, request, episode):
        if 'id' in request.data:
            del request.data['id']
        tag_names = [n for n, v in list(request.data.items()) if v]
        episode.set_tag_names(tag_names, request.user)
        return json_response(
            episode.tagging_dict(request.user)[0],
            status_code=status.HTTP_202_ACCEPTED
        )


class EpisodeViewSet(LoginRequiredViewset):
    """
    Episodes of care
    """
    base_name = 'episode'

    def list(self, request):
        return json_response(
            [e.to_dict(request.user) for e in Episode.objects.all()]
        )

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
        episode.set_tag_names(list(tagging.keys()), request.user)
        serialised = episode.to_dict(request.user)

        return json_response(
            serialised, status_code=status.HTTP_201_CREATED
        )

    @episode_from_pk
    def update(self, request, episode):
        try:
            episode.update_from_dict(request.data, request.user)
            return json_response(
                episode.to_dict(request.user, shallow=True)
            )
        except exceptions.ConsistencyError:
            return json_response({'error': 'Item has changed'}, 409)

    @episode_from_pk
    def retrieve(self, request, episode):
        return json_response(episode.to_dict(request.user))


class PatientViewSet(LoginRequiredViewset):
    base_name = 'patient'

    @patient_from_pk
    def retrieve(self, request, patient):
        PatientRecordAccess.objects.create(patient=patient, user=request.user)
        return json_response(patient.to_dict(request.user))


class PatientRecordAccessViewSet(LoginRequiredViewset):
    base_name = 'patientrecordaccess'

    def retrieve(self, request, pk=None):
        return json_response([
            a.to_dict(request.user) for a in
            PatientRecordAccess.objects.filter(patient_id=pk)
        ])


class PatientListViewSet(LoginRequiredViewset):
    base_name = 'patientlist'
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk=None):
        try:
            patientlist = PatientList.get(pk)()
        except ValueError:
            return json_response(
                {'error': 'List does not exist'},
                status_code=status.HTTP_404_NOT_FOUND
            )
        return json_response(patientlist.to_dict(request.user))


router.register('patient', PatientViewSet)
router.register('episode', EpisodeViewSet)
router.register('record', RecordViewSet)
router.register('extract-schema', ExtractSchemaViewSet)
router.register('userprofile', UserProfileViewSet)
router.register('tagging', TaggingViewSet)
router.register('patientlist', PatientListViewSet)
router.register('patientrecordaccess', PatientRecordAccessViewSet)

router.register('referencedata', ReferenceDataViewSet)
router.register('metadata', MetadataViewSet)

for subrecord in subrecords():
    sub_name = camelcase_to_underscore(subrecord.__name__)

    class SubViewSet(SubrecordViewSet):
        base_name = sub_name
        model     = subrecord

    router.register(sub_name, SubViewSet)


def register_plugin_apis():
    for plugin in plugins.OpalPlugin.list():
        for api in plugin.get_apis():
            router.register(*api)


register_plugin_apis()
