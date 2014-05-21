"""
Custom managers for query optimisations
"""
from collections import defaultdict
import time

from django.db import models


class EpisodeManager(models.Manager):

    def serialised_episode_subrecords(self, episodes, user):
        """
        Return all serialised subrecords for this set of EPISODES
        in a nested hashtable where the outer key is the episode id,
        the inner key the subrecord API name.
        """
        # CircularImport - This is used as a manager by models in this module
        from opal.models import EpisodeSubrecord, PatientSubrecord, TaggedSubrecordMixin, Tagging
        episode_subs = defaultdict(lambda: defaultdict(list))

        tag_dict = defaultdict(list)
        tags = Tagging.objects.select_related('team').filter(episode__in=episodes)
        for t in tags:
            tag_dict[t.episode_id].append(t)

        for model in EpisodeSubrecord.__subclasses__():
            name = model.get_api_name()
            subrecords = model.objects.filter(episode__in=episodes)

            for sub in subrecords:
                if issubclass(model, TaggedSubrecordMixin):
                    episode_subs[sub.episode_id][name].append(
                        sub.to_dict(user, tags=tag_dict)
                        )
                else:
                    episode_subs[sub.episode_id][name].append(sub.to_dict(user))
        return episode_subs

    def serialised_legacy(self, user):
        """
        This is a placeholder so we can run the original (1.2.2)
        get active call easily from just the manager, keeping
        the external API consistent.
        """
        episodes = set(
            list(self.filter(active=True)) +
            list(self.filter(tagging__tag_name='mine',
                             tagging__user=user))
            )
        serialised = [episode.to_dict(user)
                      for episode in episodes]
        return serialised

    def serialised_active(self, user, **kw):
        """
        Return a set of serialised active episodes.

        This is the first pass at optimising the initial active patients
        query that kicks off the list and bootstraps the app.

        Currently running at ~= 1.7s over the ~= 4.7s for the latest live
        data dump.

        KWARGS will be passed to the episode filter.
        """
#        return self.serialised_legacy(user)
        from opal.models import EpisodeSubrecord, PatientSubrecord

        filters = kw.copy()
        filters['active'] = True

        episodes = self.filter(**filters)
        patient_ids = [e.patient_id for e in episodes]
        patient_subs = defaultdict(lambda: defaultdict(list))

        episode_subs = self.serialised_episode_subrecords(episodes, user)

        for model in PatientSubrecord.__subclasses__():
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
            serialised.append(d)

            for key, value in episode_subs[e.id].items():
                d[key] = value
            for key, value in patient_subs[e.patient_id].items():
                d[key] = value
        return serialised
