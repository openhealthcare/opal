"""
Allow us to make search queries
"""
import datetime

from django.contrib.contenttypes.models import ContentType
from django.db import models as djangomodels
from django.conf import settings

from opal import models
from opal.core import fields, subrecords
from opal.utils import stringport


def get_model_name_from_column_name(column_name):
    return column_name.replace(' ', '').replace('_', '').lower()


def get_model_from_api_name(column_name):
    if column_name == "tagging":
        return models.Tagging
    else:
        return subrecords.get_subrecord_from_api_name(column_name)


class PatientSummary(object):
    def __init__(self, episode):
        self.start = episode.start
        self.end = episode.end
        self.episode_ids = set([episode.id])
        self.patient_id = episode.patient.id
        self.categories = set([episode.category_name])
        self.id = episode.patient.demographics_set.get().id

    def update(self, episode):
        if not self.start:
            self.start = episode.start
        elif episode.start:
            if self.start > episode.start:
                self.start = episode.start

        if not self.end:
            self.end = episode.end
        elif episode.end:
            if self.end < episode.end:
                self.end = episode.end

        self.episode_ids.add(episode.id)
        self.categories.add(episode.category_name)

    def to_dict(self):
        result = {k: getattr(self, k) for k in [
            "patient_id", "start", "end", "id"
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
    return [e for e in episodes if e.visible_to(user)]


class QueryBackend(object):
    """
    Base class for search implementations to inherit from
    """
    def __init__(self, user, query):
        self.user = user
        self.query = query

    def fuzzy_query(self):
        raise NotImplementedError()

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
        return [
            p.to_dict(self.user) for p in patients
        ]


class DatabaseQuery(QueryBackend):
    """
    The default built in query backend for OPAL allows advanced search
    criteria building.

    We broadly map reduce all criteria then the set of combined and/or
    criteria together, then only unique episodes.

    Finally we filter based on episode type level restrictions.
    """

    def fuzzy_query(self):
        """
        Fuzzy queries break apart the query string by spaces and search a
        number of fields based on the underlying tokens.

        We then search hospital number, first name and surname by those fields
        and order by the occurances

        so if you put in Anna Lisa, even though this is a first name split
        becasuse Anna and Lisa will both be found, this will rank higher
        than an Anna or a Lisa, although both of those will also be found
        """
        some_query = self.query
        patients = models.Patient.objects.search(some_query)
        episodes = models.Episode.objects.filter(
            patient__id__in=patients.values_list("id", flat=True)
        )
        patient_summaries = self._get_aggregate_patients_from_episodes(
            episodes
        )
        return sorted(
            patient_summaries,
            key=lambda x: x["count"],
            reverse=True
        )

    def _episodes_for_filter_kwargs(self, filter_kwargs, model):
        """
        For a given MODEL, return the Episodes that match for FILTER_KWARGS,
        understanding how to handle both EpispdeSubrecord and PatientSubrecord
        appropriately.
        """
        if issubclass(model, models.EpisodeSubrecord):
            return models.Episode.objects.filter(**filter_kwargs)
        elif issubclass(model, models.PatientSubrecord):
            pats = models.Patient.objects.filter(**filter_kwargs)
            eps = []
            for p in pats:
                eps += list(p.episode_set.all())
            return eps

    def _episodes_for_boolean_fields(self, query, field, contains):
        model = get_model_from_api_name(query['column'])
        model_name = get_model_name_from_column_name(query['column'])
        val = query['query'] == 'true'
        kw = {'{0}__{1}'.format(model_name, field): val}
        return self._episodes_for_filter_kwargs(kw, model)

    def _episodes_for_date_fields(self, query, field, contains):
        model = get_model_from_api_name(query['column'])
        model_name = get_model_name_from_column_name(query['column'])
        qtype = ''
        val = datetime.datetime.strptime(query['query'], "%d/%m/%Y")
        if query['queryType'] == 'Before':
            qtype = '__lte'
        elif query['queryType'] == 'After':
            qtype = '__gte'

        kw = {'{0}__{1}{2}'.format(model_name, field, qtype): val}
        return self._episodes_for_filter_kwargs(kw, model)

    def _episodes_for_many_to_many_fields(self, query, field_obj):
        model = get_model_from_api_name(query['column'])
        model_name = get_model_name_from_column_name(query['column'])
        related_field = query["field"].lower()
        key = "%s__%s__name" % (model_name, related_field)
        kwargs = {key: query["query"]}
        return self._episodes_for_filter_kwargs(kwargs, model)

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
        except Synonym.DoesNotExist:
            pass  # That's fine.

        kw_fk = {'{0}__{1}_fk__name{2}'.format(model.replace('_', ''),
                                               field, contains): name}
        kw_ft = {'{0}__{1}_ft{2}'.format(model.replace('_', ''),
                                         field, contains): query['query']}

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
        Mod = get_model_from_api_name(column_name)

        named_fields = [f for f in Mod._meta.fields if f.name == field]

        if len(named_fields) == 1 and isinstance(named_fields[0],
                                                 djangomodels.BooleanField):
            eps = self._episodes_for_boolean_fields(query, field, contains)

        elif len(named_fields) == 1 and isinstance(named_fields[0],
                                                   djangomodels.DateField):
            eps = self._episodes_for_date_fields(query, field, contains)

        elif hasattr(Mod, field) and isinstance(getattr(Mod, field),
                                                fields.ForeignKeyOrFreeText):
            eps = self._episodes_for_fkorft_fields(query, field, contains, Mod)

        elif hasattr(Mod, field) and isinstance(Mod._meta.get_field(field),
                                                djangomodels.ManyToManyField):
            eps = self._episodes_for_many_to_many_fields(
                query, Mod._meta.get_field(field))

        else:
            model_name = get_model_name_from_column_name(query['column'])
            queryset_path = '{0}__{1}{2}'.format(model_name, field, contains)
            kw = {queryset_path: query['query']}

            if Mod == models.Tagging:
                tag_name = query['field'].replace(" ", "_").title()
                eps = models.Episode.objects.filter(
                    tagging__value__iexact=tag_name
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
            id__in=list(patient_summaries.keys())
        )
        patients = patients.prefetch_related("demographics_set")

        results = []

        for patient_id, patient_summary in patient_summaries.items():
            patient = next(p for p in patients if p.id == patient_id)
            demographic = patient.demographics_set.get()

            result = {k: getattr(demographic, k) for k in [
                "first_name", "surname", "hospital_number", "date_of_birth"
            ]}

            result.update(patient_summary.to_dict())
            results.append(result)

        return results

    def _episodes_without_restrictions(self):
        all_matches = [
            (q['combine'], self.episodes_for_criteria(q))
            for q in self.query
        ]
        if not all_matches:
            return []

        working = set(all_matches[0][1])
        rest = all_matches[1:]

        for combine, episodes in rest:
            methods = {
                'and': 'intersection',
                'or' : 'union',
                'not': 'difference'
            }
            working = getattr(set(episodes), methods[combine])(working)

        return working

    def get_episodes(self):
        return episodes_for_user(
            self._episodes_without_restrictions(), self.user)

    def get_patient_summaries(self):
        eps = self._episodes_without_restrictions()
        episode_ids = [e.id for e in eps]

        # get all episodes of patients, that have episodes that
        # match the criteria
        all_eps = models.Episode.objects.filter(
            patient__episode__in=episode_ids
        )
        filtered_eps = episodes_for_user(all_eps, self.user)
        return self._get_aggregate_patients_from_episodes(filtered_eps)

    def get_patients(self):
        patients = set(e.patient for e in self.get_episodes())
        return list(patients)

    def description(self):
        """
        Provide a textual description of the current search
        """
        filteritem = "{combine} {column} {field} {queryType} {query}"
        filters = "\n".join(
            filteritem.format(**f) for f in self.query
        )
        return """{username} ({date})
Searching for:
{filters}
""".format(username=self.user.username,
           date=datetime.datetime.now(),
           filters=filters)


def create_query(user, criteria):
    """
        gives us a level of indirection to select the search backend we're
        going to use, without this we can get import errors if the module is
        loaded after this module
    """
    if hasattr(settings, "OPAL_SEARCH_BACKEND"):
        query_backend = stringport(settings.OPAL_SEARCH_BACKEND)
        return query_backend(user, criteria)

    return DatabaseQuery(user, criteria)
