from rest_framework import viewsets
from opal.core.views import json_response
from opal.core.pathway import Pathway
from rest_framework.permissions import IsAuthenticated
from opal.models import Patient, Episode


class PathwayApi(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def dispatch(self, *args, **kwargs):
        self.name = kwargs.pop('name', 'pathway')
        self.episode_id = kwargs.get('episode_id', None)
        self.patient_id = kwargs.get('patient_id', None)
        return super(PathwayApi, self).dispatch(*args, **kwargs)

    def create(self, request, **kwargs):
        # actually saves the pathway
        pathway = Pathway.get(self.name)()
        data = request.data

        before_patient = None
        before_episode = None

        if self.episode_id:
            before_episode = Episode.objects.get(id=self.episode_id)

        if self.patient_id:
            before_patient = Patient.objects.get(id=self.patient_id)
        patient, episode = pathway.save(
            data,
            user=request.user,
            patient=before_patient,
            episode=before_episode
        )
        redirect = pathway.redirect_url(
            user=request.user, patient=patient, episode=episode
        )

        episode_id = None

        if episode:
            episode_id = episode.id

        return json_response({
            "episode_id": episode_id,
            "patient_id": patient.id,
            "redirect_url": redirect
        })

    def retrieve(self, *args, **kwargs):
        # gets the pathways
        pathway_cls = Pathway.get(self.name)
        episode = None
        patient = None

        if self.episode_id:
            episode = Episode.objects.get(id=self.episode_id)

        if self.patient_id:
            patient = Patient.objects.get(id=self.patient_id)
        pathway = pathway_cls()
        is_modal = self.request.GET.get("is_modal", False) == "True"
        serialised = json_response(
            pathway.to_dict(
                is_modal,
                user=self.request.user,
                patient=patient,
                episode=episode
            )

        )
        return serialised
