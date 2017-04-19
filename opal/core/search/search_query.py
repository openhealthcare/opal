from opal.core.discoverable import DiscoverableFeature
from opal.utils import camelcase_to_underscore
from opal.models import Episode, deserialize_date


class SearchException(Exception):
    pass


class SearchQueryField(object):
    lookup_list = None
    enum = None
    description = None
    slug = None
    display_name = None

    def get_slug(self):
        if self.slug is not None:
            return self.slug

        if self.display_name is None:
            raise ValueError(
                'Must set display_name for {0}'.format(self)
            )
        return camelcase_to_underscore(self.display_name).replace(' ', '')

    def get_display_name(self):
        return self.display_name

    def to_dict(self):
        return dict(
            name=self.get_slug(),
            title=self.display_name,
            type=self.field_type,
            enum=self.enum,
            lookup_list=self.lookup_list,
            description=self.description
        )

    def query(self, given_query):
        """
            takes in the full query and returns a list of episodes
        """
        raise NotImplementedError("please implement a query")


class SearchQuery(DiscoverableFeature):
    module_name = "search_query"
    fields = []

    def get_fields(self):
        return self.fields

    def to_dict(self):
        return dict(
            name=self.get_slug(),
            display_name=self.display_name,
            advanced_searchable=True,
            fields=[i().to_dict() for i in self.get_fields()]
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
            f() for f in self.get_fields() if f().get_slug() == given_field
        )
        return query_field.query(given_query)


class EpisodeStart(SearchQueryField):
    display_name = "Start"
    description = "Episode Start"
    field_type = "date_time"

    def query(self, given_query):
        val = deserialize_date(given_query['query'])
        if given_query['queryType'] == 'Before':
            return (i for i in Episode.objects.all() if i.start <= val)
        elif given_query['queryType'] == 'After':
            return (i for i in Episode.objects.all() if i.start >= val)
        else:
            err = "unrecognised query type for the start episode query with {}"
            raise SearchException(err.format(given_query['queryType']))


class EpisodeEnd(SearchQueryField):
    display_name = "End"
    description = "Episode End"
    field_type = "date_time"

    def query(self, given_query):
        val = deserialize_date(given_query['query'])
        if given_query['queryType'] == 'Before':
            return (i for i in Episode.objects.all() if i.end <= val)
        elif given_query['queryType'] == 'After':
            return (i for i in Episode.objects.all() if i.end >= val)
        else:
            err = "unrecognised query type for the end episode query with {}"
            raise SearchException(err.format(given_query['queryType']))


class EpisodeQuery(SearchQuery):
    display_name = "Episode"
    slug = "episode"
    fields = (EpisodeStart, EpisodeEnd,)
