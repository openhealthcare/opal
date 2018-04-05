"""
Custom managers for query optimisations
"""
from collections import defaultdict
import operator

from django.db import models
from django.db.models import Q

from opal.core.subrecords import (
    episode_subrecords, patient_subrecords
)
from functools import reduce


class PatientQueryset(models.QuerySet):
    def search(self, some_query):
        """
        splits a string by space and queries
        first name, last name and hospital number
        """
        fields = ["hospital_number", "first_name", "surname"]

        query_values = some_query.split(" ")
        qs = self
        for query_value in query_values:
            q_objects = []
            for field in fields:
                model_field = "demographics__{}__icontains".format(field)
                q_objects.append(Q(**{model_field: query_value}))
            qs = qs.filter(reduce(operator.or_, q_objects))
        return qs


class EpisodeQueryset(models.QuerySet):

    def search(self, some_query):
        from opal.models import Patient
        patients = Patient.objects.search(some_query).values_list(
            "id", flat=True
        )
        return self.filter(patient_id__in=patients)

    def serialised_episode_subrecords(self, episodes, user):
        """
        Return all serialised subrecords for this set of EPISODES
        in a nested hashtable where the outer key is the episode id,
        the inner key the subrecord API name.
        """
        episode_subs = defaultdict(lambda: defaultdict(list))

        for model in episode_subrecords():
            name = model.get_api_name()
            subrecords = model.objects.filter(episode__in=episodes)

            for related in model._meta.many_to_many:
                subrecords = subrecords.prefetch_related(related.attname)

            for sub in subrecords:
                episode_subs[sub.episode_id][name].append(sub.to_dict(user))
        return episode_subs

    def serialised(self, user, episodes,
                   historic_tags=False, episode_history=False):
        """
        Return a set of serialised EPISODES.

        If HISTORIC_TAGS is Truthy, return deleted tags as well.
        If EPISODE_HISTORY is Truthy return historic episodes as well.
        """
        patient_ids = [e.patient_id for e in episodes]
        patient_subs = defaultdict(lambda: defaultdict(list))

        episode_subs = self.serialised_episode_subrecords(episodes, user)
        for model in patient_subrecords():
            name = model.get_api_name()
            subrecords = model.objects.filter(patient__in=patient_ids)

            for sub in subrecords:
                patient_subs[sub.patient_id][name].append(sub.to_dict(user))

        # We do this here because it's an order of magnitude quicker than
        # hitting episode.tagging_dict() for each episode in a loop.
        taggings = defaultdict(dict)
        from opal.models import Tagging
        qs = Tagging.objects.filter(episode__in=episodes)

        if not historic_tags:
            qs = qs.filter(archived=False)

        for tag in qs:
            if tag.value == 'mine' and tag.user != user:
                continue
            taggings[tag.episode_id][tag.value] = True

        serialised = []

        for e in episodes:
            d = e.to_dict(user, shallow=True)

            for key, value in list(episode_subs[e.id].items()):
                d[key] = value
            for key, value in list(patient_subs[e.patient_id].items()):
                d[key] = value

            d['tagging'] = [taggings[e.id]]
            d['tagging'][0]['id'] = e.id
            serialised.append(d)

            if episode_history:
                d['episode_history'] = e._episode_history_to_dict(user)

        return serialised

    def serialised_active(self, user, **kw):
        """
        Return a set of serialised active episodes.

        KWARGS will be passed to the episode filter.
        """
        filters = kw.copy()
        filters['active'] = True
        episodes = self.filter(**filters)
        as_dict = self.serialised(user, episodes)
        return as_dict
