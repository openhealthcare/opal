"""
Allow us to make search queries
"""
import datetime

from django.contrib.contenttypes.models import ContentType
from django.db import models as djangomodels


from opal import models
from opal.core import fields


def get_model_name_from_column_name(column_name):
    return column_name.replace(' ', '').replace('_', '').lower()


def get_model_from_column_name(column_name):
    Mod = None
    model_name = get_model_name_from_column_name(column_name)

    for m in djangomodels.get_models():
        if m.__name__.lower() == model_name:
            if not Mod:
                Mod = m
            elif (issubclass(m, models.EpisodeSubrecord) or
                  issubclass(m, models.PatientSubrecord)):
                Mod = m

    return Mod


class PatientSummary(object):
    def __init__(self, episode):
        self.start_date = episode.start_date
        self.end_date = episode.end_date
        self.episode_ids = set([episode.id])
        self.episode_id = episode.id
        self.categories = set([episode.category])
        self.id = episode.patient.demographics_set.get().id

    def update(self, episode):
        if not self.start_date:
            self.start_date = episode.start_date
        elif episode.start_date:
            if self.start_date > episode.start_date:
                self.start_date = episode.start_date

        if not self.end_date:
            self.end_date = episode.end_date
        elif episode.end_date:
            if self.end_date < episode.end_date:
                self.end_date = episode.end_date

        self.episode_ids.add(episode.id)
        self.categories.add(episode.category)

    def to_dict(self):
        result = {k: getattr(self, k) for k in [
            "episode_id", "start_date", "end_date", "id"
        ]}
        result["categories"] = sorted(self.categories)
        result["count"] = len(self.episode_ids)
        return result


def episodes_for_user(episodes, user):
    """
    Given an iterable of EPISODES and a USER, return a filtered
    list of episodes that this user has the permissions to know
    about.
    """
    teams = models.Team.restricted_teams(user)
    allowed_episodes = []
    for e in episodes:
        allowed = False
        if e.tagging_set.count() == 0:
            allowed_episodes.append(e)
            continue
        for tagging in e.tagging_set.all():
            if not tagging.team.restricted:
                allowed = True
                break
            elif tagging.team in teams:
                allowed = True
                break

        if allowed:
            allowed_episodes.append(e)
    return allowed_episodes


class QueryBackend(object):
    """
    Base class for search implementations to inherit from
    """
    def __init__(self, user, query):
        self.user = user
        self.query = query

    def get_episodes(self):
        raise NotImplementedError()

    def description(self):
        raise NotImplementedError()

    def get_patients(self):
        raise NotImplementedError()

    def get_patient_summaries(self):
        raise NotImplementedError()

    def patients_as_json(self):
        patients = self.get_patients()
        return [p.to_dict(self.user) for p in patients]


class DatabaseQuery(QueryBackend):
    """
    The default built in query backend for OPAL allows advanced search
    criteria building.

    We broadly map reduce all criteria then the set of combined and/or
    criteria together, then only unique episodes.

    Finally we filter based on team restrictions.
    """

    def _episodes_for_boolean_fields(self, query, field, contains):
        model = get_model_name_from_column_name(query['column'])
        val = query['query'] == 'true'
        kw = {'{0}__{1}'.format(model.replace('_', ''), field): val}
        eps = models.Episode.objects.filter(**kw)
        return eps

    def _episodes_for_date_fields(self, query, field, contains):
        model = get_model_name_from_column_name(query['column'])
        qtype = ''
        val = datetime.datetime.strptime(query['query'], "%d/%m/%Y")
        if query['queryType'] == 'Before':
            qtype = '__lte'
        elif query['queryType'] == 'After':
            qtype = '__gte'

        kw = {'{0}__{1}{2}'.format(model, field, qtype): val}
        eps = models.Episode.objects.filter(**kw)
        return eps

    def _episodes_for_many_to_many_fields(self, query, field_obj):
        model = get_model_name_from_column_name(query['column'])
        related_field = query["field"].lower()
        key = "%s__%s__name" % (model, related_field)
        kwargs = {key: query["query"]}
        return models.Episode.objects.filter(**kwargs)

    def _episodes_for_fkorft_fields(self, query, field, contains, Mod):
        model = get_model_name_from_column_name(query['column'])

        # Look up to see if there is a synonym.
        content_type = ContentType.objects.get_for_model(
            getattr(Mod, field).foreign_model)
        name = query['query']
        try:
            from opal.models import Synonym
            synonym = Synonym.objects.get(content_type=content_type, name=name)
            name = synonym.content_object.name
        except Synonym.DoesNotExist: # maybe this is pointless exception bouncing?
            pass # That's fine.

        kw_fk = {'{0}__{1}_fk__name{2}'.format(model.replace('_', ''), field, contains): name}
        kw_ft = {'{0}__{1}_ft{2}'.format(model.replace('_', ''), field, contains): query['query']}

        if issubclass(Mod, models.EpisodeSubrecord):

            qs_fk = models.Episode.objects.filter(**kw_fk)
            qs_ft = models.Episode.objects.filter(**kw_ft)
            eps = set(list(qs_fk) + list(qs_ft))

        elif issubclass(Mod, models.PatientSubrecord):
            qs_fk = models.Patient.objects.filter(**kw_fk)
            qs_ft = models.Patient.objects.filter(**kw_ft)
            pats = set(list(qs_fk) + list(qs_ft))
            eps = []
            for p in pats:
                eps += list(p.episode_set.all())
        return eps

    def episodes_for_criteria(self, criteria):
        """
        Given one set of criteria, return episodes that match it.
        """
        query = criteria
        querytype = query['queryType']
        contains = '__iexact'
        if querytype == 'Contains':
            contains = '__icontains'

        column_name = query['column']

        field = query['field'].replace(' ', '_').lower()
        Mod = get_model_from_column_name(column_name)

        if column_name.lower() == 'tags':
            Mod = models.Tagging

        named_fields = [f for f in Mod._meta.fields if f.name == field]

        if len(named_fields) == 1 and isinstance(named_fields[0],djangomodels.BooleanField):
            eps = self._episodes_for_boolean_fields(query, field, contains)

        elif len(named_fields) == 1 and isinstance(named_fields[0], djangomodels.DateField):
            eps = self._episodes_for_date_fields(query, field, contains)

        elif hasattr(Mod, field) and isinstance(getattr(Mod, field), fields.ForeignKeyOrFreeText):
            eps = self._episodes_for_fkorft_fields(query, field, contains, Mod)
        elif hasattr(Mod, field) and isinstance(Mod._meta.get_field(field), djangomodels.ManyToManyField):
            eps = self._episodes_for_many_to_many_fields(query, Mod._meta.get_field(field))
        else:
            model_name = get_model_name_from_column_name(query['column'])
            kw = {'{0}__{1}{2}'.format(model_name, field, contains): query['query']}

            if Mod == models.Tagging:
                tag_name = query['field'].replace(" ", "_").title()
                eps = models.Episode.objects.filter(
                    tagging__team__name__iexact=tag_name
                )

            elif issubclass(Mod, models.EpisodeSubrecord):
                eps = models.Episode.objects.filter(**kw)
            elif issubclass(Mod, models.PatientSubrecord):
                pats = models.Patient.objects.filter(**kw)
                eps = []
                for p in pats:
                    eps += list(p.episode_set.all())
        return eps

    def _get_aggregate_patients_from_episodes(self, episodes):
        # at the moment we use date_of_admission/discharge only if
        # date_of_episode is null, because of this we can't do this
        # in a vanilla orm query
        patient_summaries = {}

        for episode in episodes:
            patient_id = episode.patient_id
            if patient_id in patient_summaries:
                patient_summaries[patient_id].update(episode)
            else:
                patient_summaries[patient_id] = PatientSummary(episode)

        patients = models.Patient.objects.filter(
            id__in=patient_summaries.keys()
        )
        patients = patients.prefetch_related("demographics_set")

        results = []

        for patient_id, patient_summary in patient_summaries.iteritems():
            patient = next(p for p in patients if p.id == patient_id)
            demographic = patient.demographics_set.get()

            result = {k: getattr(demographic, k) for k in [
                "name", "hospital_number", "date_of_birth"
                ]}

            result.update(patient_summary.to_dict())
            results.append(result)

        return results

    def _filter_for_restricted_only(self, episodes):
        """
        Given an iterable of EPISODES, return those for which our
        current restricted only user is allowed to know about.
        """
        teams = models.Team.restricted_teams(self.user)
        allowed_episodes = []
        for e in episodes:
            for tagging in e.tagging_set.all():
                if tagging.team in teams:
                    allowed_episodes.append(e)
                    break

        return allowed_episodes

    def _filter_restricted_teams(self, episodes):
        """
        Given an iterable of EPISODES, return only those which
        are not only members of restricted teams that our user is not
        allowed to know about.
        """
        return episodes_for_user(episodes, self.user)

    def _episodes_without_restrictions(self):
        all_matches = [(q['combine'], self.episodes_for_criteria(q))
                       for q in self.query]
        if not all_matches:
            return []

        working = set(all_matches[0][1])
        rest = all_matches[1:]

        for combine, episodes in rest:
            methods = {'and': 'intersection', 'or': 'union', 'not': 'difference'}
            working = getattr(set(episodes), methods[combine])(working)

        return working

    def _filter_restricted_episodes(self, eps):
        if self.user.profile.restricted_only:
            eps = self._filter_for_restricted_only(eps)
        else:
            eps = self._filter_restricted_teams(eps)

        return eps

    def get_episodes(self):
        eps = self._episodes_without_restrictions()
        return self._filter_restricted_episodes(eps)

    def get_patient_summaries(self):
        eps = self._episodes_without_restrictions()
        episode_ids = [e.id for e in eps]

        # get all episodes of patients, that have episodes that
        # match the criteria
        all_eps = models.Episode.objects.filter(
            patient__episode__in=episode_ids
        )
        filtered_eps = self._filter_restricted_episodes(all_eps)
        return self._get_aggregate_patients_from_episodes(filtered_eps)

    def get_patients(self):
        patients = set(e.patient for e in self.get_episodes())
        return list(patients)

    def description(self):
        """
        Provide a textual description of the current search
        """
        filters = "\n".join("{combine} {column} {field} {queryType} {query}".format(**f) for f in self.query)
        return """{username} ({date})
Searching for:
{filters}
""".format(username=self.user.username, date=datetime.datetime.now(), filters=filters)


SearchBackend = DatabaseQuery
