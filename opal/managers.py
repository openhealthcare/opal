"""
Custom managers for query optimisations
"""
from collections import defaultdict
import time

from django.db import models

from opal.utils.models import episode_subrecords, patient_subrecords

class EpisodeManager(models.Manager):

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

            for sub in subrecords:
                episode_subs[sub.episode_id][name].append(sub.to_dict(user))
        return episode_subs

    def serialised(self, user, episodes, historic_tags=False):
        """
        Return a set of serialised EPISODES.

        If HISTORIC_TAGS is Truthy, return delted tags as well.
        """
        patient_ids = [e.patient_id for e in episodes]
        patient_subs = defaultdict(lambda: defaultdict(list))

        episode_subs = self.serialised_episode_subrecords(episodes, user)

        for model in patient_subrecords():
            name = model.get_api_name()
            subrecords = model.objects.filter(patient__in=patient_ids)
            for sub in subrecords:
                patient_subs[sub.patient_id][name].append(sub.to_dict(user))


        serialised = []
        for e in episodes:
            d = {
                'id'               : e.id,
                'active'           : e.active,
                'date_of_admission': e.date_of_admission,
                'discharge_date'   : e.discharge_date,
                'consistency_token': e.consistency_token
                }

            for key, value in episode_subs[e.id].items():
                d[key] = value
            for key, value in patient_subs[e.patient_id].items():
                d[key] = value
            d['tagging'] = e.tagging_dict(user)
            serialised.append(d)

        if historic_tags:
            episode_ids = [e.id for e in episodes]
            historic = Tagging.historic_tags_for_episodes(episode_ids)
            for episode in serialised:
                if episode['id'] in historic:
                    historic_tags = historic[episode['id']]
                    for t in historic_tags.keys():
                        episode['tagging'][0][t] = True

        return serialised

    def serialised_active(self, user, **kw):
        """
        Return a set of serialised active episodes.

        KWARGS will be passed to the episode filter.
        """
        filters = kw.copy()
        filters['active'] = True
        episodes = self.filter(**filters)
        return self.serialised(user, episodes)

    def ever_tagged(self, team):
        """
        Return a list of episodes that were ever tagged to TEAM
        """
        from opal.models import Tagging

        team_name = team.lower().replace(' ', '_')
        current = self.filter(tagging__team__name=team_name)
        historic = Tagging.historic_episodes_for_tag(team_name)
        return list(historic) + list(current)
