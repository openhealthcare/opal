from opal.core.discoverable import DiscoverableFeature
from opal.core.exceptions import Error
from opal.utils import camelcase_to_underscore
from opal.models import Episode, Tagging, deserialize_date


class SearchException(Error):
    pass


class SearchRuleField(object):
    lookup_list = None
    enum = None
    description = None
    slug = None
    display_name = None

    @classmethod
    def get_slug(klass):
        if klass.slug is not None:
            return klass.slug

        if klass.display_name is None:
            raise ValueError(
                'Must set display_name for {0}'.format(klass)
            )
        return camelcase_to_underscore(klass.display_name).replace(' ', '')

    def to_dict(self):
        return dict(
            name=self.get_slug(),
            title=self.display_name,
            type=self.field_type,
            enum=self.enum,
            type_display_name=self.type_display_name,
            lookup_list=self.lookup_list,
            description=self.description
        )

    def query(self, given_query):
        """
            takes in the full query and returns a list of episodes
        """
        raise NotImplementedError("please implement a query")


class SearchRule(DiscoverableFeature):
    module_name = "search_rule"
    fields = []

    def get_fields(self):
        return self.fields

    def to_dict(self):
        return dict(
            name=self.get_slug(),
            display_name=self.display_name,
            fields=[i().to_dict() for i in self.get_fields()],
            description=getattr(self, "description", None)
        )

    @classmethod
    def get(klass, name):
        """
        Return a specific subclass by slug
        """
        for sub in klass.list():
            if sub.get_slug() == name:
                return sub

    def query(self, given_query):
        given_field = given_query['field']
        query_field = next(
            f for f in self.get_fields() if f.get_slug() == given_field
        )
        return query_field().query(given_query)


class EpisodeStart(SearchRuleField):
    display_name = "Start"
    description = "Episode Start"
    field_type = "date_time"
    type_display_name = "Date & Time"

    def query(self, given_query):
        val = deserialize_date(given_query['query'])
        qs = Episode.objects.exclude(start=None)
        if given_query['queryType'] == 'Before':
            return qs.filter(start__lte=val)
        elif given_query['queryType'] == 'After':
            return qs.filter(start__gte=val)
        else:
            err = "unrecognised query type for the start episode query with {}"
            raise SearchException(err.format(given_query['queryType']))


class EpisodeEnd(SearchRuleField):
    display_name = "End"
    description = "Episode End"
    field_type = "date_time"
    type_display_name = "Date & Time"

    def query(self, given_query):
        val = deserialize_date(given_query['query'])
        qs = Episode.objects.exclude(end=None)
        if given_query['queryType'] == 'Before':
            return qs.filter(end__lte=val)
        elif given_query['queryType'] == 'After':
            return qs.filter(end__gte=val)
        else:
            err = "unrecognised query type for the start episode query with {}"
            raise SearchException(err.format(given_query['queryType']))


class EpisodeTeam(SearchRuleField):
    ALL_OF = "All Of"
    ANY_OF = "Any Of"

    display_name = "Team"
    description = "The team(s) related to an episode of care"
    field_type = "many_to_many_multi_select"
    type_display_name = "Text Field"

    @property
    def enum(self):
        return [i["title"] for i in Tagging.build_field_schema()]

    def translate_titles_to_names(self, titles):
        result = []
        titles_not_found = set(titles)
        for schema in Tagging.build_field_schema():
            if schema["title"] in titles:
                result.append(schema["name"])
                titles_not_found.remove(schema["title"])

        if titles_not_found:
            raise SearchException(
                "unable to find the tag titled {}".format(
                    ",".join(titles_not_found)
                )
            )

        return result

    def query(self, given_query):
        query_type = given_query["queryType"]
        team_display_names = given_query['query']
        if not query_type == self.ALL_OF:
            if not query_type == self.ANY_OF:
                err = """
                    unrecognised query type for the episode team query with {}
                """.strip()
                raise SearchException(err.format(query_type))

        team_names = self.translate_titles_to_names(team_display_names)
        qs = Episode.objects.all()
        if given_query["queryType"] == self.ALL_OF:
            for team_name in team_names:
                qs = qs.filter(tagging__value=team_name)
        else:
            qs = qs.filter(tagging__value__in=team_names)

        return qs.distinct()


class EpisodeQuery(SearchRule):
    display_name = "Episode"
    slug = "episode"
    fields = (EpisodeStart, EpisodeEnd, EpisodeTeam,)
