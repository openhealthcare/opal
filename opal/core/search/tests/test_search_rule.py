from mock import MagicMock, patch
import datetime

from opal.core.test import OpalTestCase
from opal.core.search import search_rule


class SearchRuleFieldTestCase(OpalTestCase):
    def setUp(self, *args, **kwargs):
        class SomeSearchRuleField(search_rule.SearchRuleField):
            lookup_list = "some_list"
            enum = [1, 2, 3]
            description = "its a custom field"
            display_name = "custom field you know"
            field_type = "string"
            slug = "some_slug"
            type_display_name = "some field"
        self.custom_field = SomeSearchRuleField()
        super(SearchRuleFieldTestCase, self).setUp(*args, **kwargs)

    def test_slug_if_slug_provided(self):
        self.assertEqual(self.custom_field.get_slug(), "some_slug")

    def test_slug_if_slug_not_provided(self):
        class SomeOtherSearchRuleField(search_rule.SearchRuleField):
            lookuplist = "some_list"
            enum = [1, 2, 3]
            description = "its a custom field"
            display_name = "custom field you know"
            type_display_name = "some field"
        self.assertEqual(
            SomeOtherSearchRuleField().get_slug(), "customfieldyouknow"
        )

    def test_slug_if_no_slug_or_display_name(self):
        class SluglessSearchRuleField(search_rule.SearchRuleField):
            description = "Invalid for slugs"
        with self.assertRaises(ValueError):
            SluglessSearchRuleField.get_slug()

    def test_query(self):
        with self.assertRaises(NotImplementedError) as nie:
            self.custom_field.query("some query")

        self.assertEqual("please implement a query", str(nie.exception))

    def test_to_dict(self):
        expected = dict(
            lookup_list="some_list",
            enum=[1, 2, 3],
            description="its a custom field",
            name="some_slug",
            title='custom field you know',
            type="string",
            type_display_name="some field"
        )
        self.assertEqual(
            self.custom_field.to_dict(),
            expected
        )


class SearchRuleTestCase(OpalTestCase):
    def test_get(self):
        some_mock_query = MagicMock()
        with patch.object(search_rule.SearchRule, "list") as get_list:
            get_list.return_value = [some_mock_query]
            some_mock_query.get_slug.return_value = "tree"
            result = search_rule.SearchRule.get("tree")
            self.assertEqual(result, some_mock_query)

    def test_get_if_missing(self):
        some_mock_query = MagicMock()
        with patch.object(search_rule.SearchRule, "list") as get_list:
            get_list.return_value = [some_mock_query]
            some_mock_query.get_slug.return_value = "tree"
            result = search_rule.SearchRule.get("onion")
            self.assertIsNone(result)

    def test_get_fields(self):
        self.assertEqual(search_rule.SearchRule().get_fields(), [])

    def test_query(self):
        some_mock_query = MagicMock()

        with patch.object(
            search_rule.SearchRule, "get_fields"
        ) as get_fields:
            get_fields.return_value = [some_mock_query]
            some_mock_query.get_slug.return_value = "tree"
            some_mock_query().query.return_value = "some_result"
            query = dict(field="tree")
            result = search_rule.SearchRule().query(query)
            self.assertEqual(result, "some_result")
            some_mock_query().query.assert_called_once_with(query)

    def test_to_dict(self):
        class SomeSearchRule(search_rule.SearchRule):
            description = "its a custom rule"
            display_name = "custom field you know"
            slug = "some_slug"
            fields = []

        expected = dict(
            description="its a custom rule",
            display_name="custom field you know",
            name="some_slug",
            fields=[]
        )
        self.assertEqual(SomeSearchRule().to_dict(), expected)


class EpisodeQueryTestCase(OpalTestCase):
    def setUp(self, *args, **kwargs):
        super(EpisodeQueryTestCase, self).setUp(*args, **kwargs)
        _, self.episode = self.new_patient_and_episode_please()
        self.episode.start = datetime.date(2017, 1, 1)
        self.episode.end = datetime.date(2017, 1, 5)
        self.episode.save()
        self.episode_query = search_rule.EpisodeQuery()

    def test_episode_end_start(self):
        query_end = dict(
            queryType="Before",
            query="1/8/2017",
            field="end"
        )
        self.assertEqual(
            list(self.episode_query.query(query_end))[0], self.episode
        )

    def test_episode_end_when_none(self):
        self.episode.end = None
        self.episode.save()
        query_end = dict(
            queryType="Before",
            query="1/8/2017",
            field="end"
        )
        self.assertEqual(
            list(self.episode_query.query(query_end)), []
        )

    def test_episode_end_after(self):
        query_end = dict(
            queryType="After",
            query="1/8/2015",
            field="end"
        )
        self.assertEqual(
            list(self.episode_query.query(query_end))[0], self.episode
        )

    def test_episode_end_not_found(self):
        query_end = dict(
            queryType="Before",
            query="1/8/2010",
            field="end"
        )
        self.assertEqual(
            list(self.episode_query.query(query_end)), []
        )

    def test_episode_end_wrong_query_param(self):
        query_end = dict(
            queryType="asdfsadf",
            query="1/8/2010",
            field="end"
        )
        with self.assertRaises(search_rule.SearchException):
            self.episode_query.query(query_end)

    def test_episode_start_before(self):
        query_end = dict(
            queryType="Before",
            query="1/8/2017",
            field="start"
        )
        self.assertEqual(
            list(self.episode_query.query(query_end))[0], self.episode
        )

    def test_episode_start_after(self):
        query_end = dict(
            queryType="After",
            query="1/8/2015",
            field="start"
        )
        self.assertEqual(
            list(self.episode_query.query(query_end))[0], self.episode
        )

    def test_episode_start_when_none(self):
        self.episode.start = None
        self.episode.save()
        query_end = dict(
            queryType="Before",
            query="1/8/2017",
            field="start"
        )
        self.assertEqual(
            list(self.episode_query.query(query_end)), []
        )

    def test_episode_start_not_found(self):
        query_end = dict(
            queryType="Before",
            query="1/8/2011",
            field="start"
        )
        self.assertEqual(
            list(self.episode_query.query(query_end)), []
        )

    def test_episode_start_wrong_query_param(self):
        query_end = dict(
            queryType="asdfsadf",
            query="1/8/2010",
            field="start"
        )
        with self.assertRaises(search_rule.SearchException):
            self.episode_query.query(query_end)


class EpisodeTeamQueryTestCase(OpalTestCase):
    def setUp(self, *args, **kwargs):
        super(EpisodeTeamQueryTestCase, self).setUp(*args, **kwargs)
        _, self.episode_1 = self.new_patient_and_episode_please()
        _, self.episode_2 = self.new_patient_and_episode_please()
        _, self.episode_3 = self.new_patient_and_episode_please()
        self.episode_query = search_rule.EpisodeQuery()

    def test_episode_team_wrong_query_param(self):
        query_end = dict(
            queryType="asdfsadf",
            query=["Some Team"],
            field="team"
        )
        with self.assertRaises(search_rule.SearchException) as er:
            self.episode_query.query(query_end)
        self.assertEqual(
            str(er.exception),
            "unrecognised query type for the episode team query with asdfsadf"
        )

    def test_episode_team_unknown_team(self):
        query_end = dict(
            queryType="Any Of",
            query=["Some Team"],
            field="team"
        )
        with self.assertRaises(search_rule.SearchException) as er:
            self.episode_query.query(query_end)
        self.assertEqual(
            str(er.exception),
            "unable to find the tag titled Some Team"
        )

    def test_episode_team_all_of_one(self):
        """
            test all of with a single tag
        """
        self.episode_1.tagging_set.create(value="tree", archived=False)
        self.episode_1.tagging_set.create(value="plant", archived=False)
        self.episode_2.tagging_set.create(value="plant", archived=False)
        self.episode_3.tagging_set.create(value="tree", archived=False)
        query_end = dict(
            queryType="All Of",
            query=["Plant"],
            field="team"
        )
        with patch.object(search_rule.Tagging, "build_field_schema") as bfs:
            bfs.return_value = [
                dict(
                    name="plant",
                    title="Plant"
                ),
                dict(
                    name="tree",
                    title="Tree"
                ),
            ]
            result = self.episode_query.query(query_end)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].id, self.episode_1.id)
        self.assertEqual(result[1].id, self.episode_2.id)

    def test_episode_team_all_of_archived(self):
        """
            test archived tags are returned
        """
        self.episode_1.tagging_set.create(value="plant", archived=True)
        query_end = dict(
            queryType="All Of",
            query=["Plant"],
            field="team"
        )
        with patch.object(search_rule.Tagging, "build_field_schema") as bfs:
            bfs.return_value = [
                dict(
                    name="plant",
                    title="Plant"
                ),
                dict(
                    name="tree",
                    title="Tree"
                ),
            ]
            result = self.episode_query.query(query_end)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, self.episode_1.id)

    def test_episode_team_all_of_many(self):
        """
            test when looking for multiple tags only
            episodes with all of those tags will be returned
        """
        self.episode_1.tagging_set.create(value="tree", archived=False)
        self.episode_1.tagging_set.create(value="plant", archived=False)
        self.episode_2.tagging_set.create(value="plant", archived=False)
        self.episode_3.tagging_set.create(value="tree", archived=False)
        query_end = dict(
            queryType="All Of",
            query=["Plant", "Tree"],
            field="team"
        )
        with patch.object(search_rule.Tagging, "build_field_schema") as bfs:
            bfs.return_value = [
                dict(
                    name="plant",
                    title="Plant"
                ),
                dict(
                    name="tree",
                    title="Tree"
                ),
            ]
            result = self.episode_query.query(query_end)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, self.episode_1.id)

    def test_episide_team_any_of_one(self):
        """
            test all of with a single tag
        """
        self.episode_1.tagging_set.create(value="tree", archived=False)
        self.episode_1.tagging_set.create(value="plant", archived=False)
        self.episode_2.tagging_set.create(value="plant", archived=False)
        self.episode_3.tagging_set.create(value="tree", archived=False)
        query_end = dict(
            queryType="Any Of",
            query=["Plant"],
            field="team"
        )
        with patch.object(search_rule.Tagging, "build_field_schema") as bfs:
            bfs.return_value = [
                dict(
                    name="plant",
                    title="Plant"
                ),
                dict(
                    name="tree",
                    title="Tree"
                ),
            ]
            result = self.episode_query.query(query_end)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].id, self.episode_1.id)
        self.assertEqual(result[1].id, self.episode_2.id)

    def test_episide_team_any_of_many(self):
        """
            test when looking for multiple tags only
            episodes with all of those tags will be returned
        """
        self.episode_1.tagging_set.create(value="tree", archived=False)
        self.episode_1.tagging_set.create(value="plant", archived=False)
        self.episode_2.tagging_set.create(value="plant", archived=False)
        self.episode_3.tagging_set.create(value="tree", archived=False)
        query_end = dict(
            queryType="Any Of",
            query=["Plant", "Tree"],
            field="team"
        )
        with patch.object(search_rule.Tagging, "build_field_schema") as bfs:
            bfs.return_value = [
                dict(
                    name="plant",
                    title="Plant"
                ),
                dict(
                    name="tree",
                    title="Tree"
                ),
            ]
            result = self.episode_query.query(query_end)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].id, self.episode_1.id)
        self.assertEqual(result[1].id, self.episode_2.id)
        self.assertEqual(result[2].id, self.episode_3.id)
