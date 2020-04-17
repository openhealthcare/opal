import json
from opal.core.test import OpalTestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
from opal.core.pathway.tests.pathway_test import pathways as test_pathways


@patch("opal.core.pathway.Pathway.get")
class PathwaySaveViewTestCase(OpalTestCase):
    def setUp(self):
        self.patient, self.episode = self.new_patient_and_episode_please()
        self.fake_pathway_instance = MagicMock()
        self.fake_pathway = MagicMock(return_value=self.fake_pathway_instance)
        self.fake_pathway_instance.save.return_value = (
            self.patient, self.episode,
        )
        self.fake_pathway_instance.redirect_url.return_value = "/"
        self.fake_pathway_instance.to_dict.return_value = {}

    def test_no_arguments_passed_through(
        self, fake_pathway_get
    ):
        fake_pathway_get.return_value = self.fake_pathway
        url = reverse("pathway", kwargs=dict(
            name="fake",
        ))

        self.assertTrue(
            self.client.login(
                username=self.user.username, password=self.PASSWORD
            )
        )

        self.post_json(url, {})
        self.fake_pathway.assert_called_once_with()

    def test_integration(self, fake_pathway_get):
        fake_pathway_get.return_value = test_pathways.PagePathwayExample
        url = reverse("pathway", kwargs=dict(
            name="dog_owner",
            patient_id=self.patient.id,
            episode_id=self.episode.id
        ))
        post_dict = dict(
            demographics=[dict(
                first_name="James",
                surname="Watson"
            )],
            diagnosis=[dict(
                condition="Headache"
            )]
        )
        self.assertTrue(
            self.client.login(
                username=self.user.username, password=self.PASSWORD
            )
        )
        response = self.post_json(url, post_dict)
        expected = {
            'patient_id': self.patient.id,
            'redirect_url': u'/#/patient/{}/{}'.format(
                self.patient.id, self.episode.id
            ),
            'episode_id': self.episode.id
        }
        self.assertEqual(json.loads(response.content.decode('utf8')), expected)


@patch("opal.core.pathway.pathways.Pathway.get")
class PathwayGetTestCase(OpalTestCase):
    def setUp(self):
        self.patient, self.episode = self.new_patient_and_episode_please()
        self.fake_pathway_instance = MagicMock()
        pp = test_pathways.PagePathwayExample()
        self.fake_pathway_instance.to_dict.return_value = pp.to_dict(False)
        self.fake_pathway = MagicMock(return_value=self.fake_pathway_instance)

    def get_json(self, url):
        return self.client.get(
            url, content_type='application/json'
        )

    def test_retrieve_episode_no_patient(self, fake_pathway_get):
        fake_pathway_get.return_value = self.fake_pathway
        url = reverse("pathway", kwargs=dict(
            name="dog_owner",
            patient_id=self.patient.id,
        ))
        self.assertTrue(
            self.client.login(
                username=self.user.username, password=self.PASSWORD
            )
        )
        response = self.get_json(url)
        self.assertEqual(response.status_code, 200)
        self.fake_pathway_instance.to_dict.assert_called_once_with(
            False,
            user=self.user,
            patient=self.patient,
            episode=None
        )

    def test_retrieve_no_patient_or_episode(self, fake_pathway_get):
        fake_pathway_get.return_value = self.fake_pathway
        url = reverse("pathway", kwargs=dict(
            name="dog_owner",
        ))
        self.assertTrue(
            self.client.login(
                username=self.user.username, password=self.PASSWORD
            )
        )
        response = self.get_json(url)
        self.assertEqual(response.status_code, 200)
        self.fake_pathway_instance.to_dict.assert_called_once_with(
            False,
            user=self.user,
            patient=None,
            episode=None
        )

    def test_retrieve_non_modal(self, fake_pathway_get):
        fake_pathway_get.return_value = self.fake_pathway
        url = reverse("pathway", kwargs=dict(
            name="dog_owner",
            patient_id=self.patient.id,
            episode_id=self.episode.id
        ))
        self.assertTrue(
            self.client.login(
                username=self.user.username, password=self.PASSWORD
            )
        )
        response = self.get_json(url)
        self.assertEqual(response.status_code, 200)
        self.fake_pathway_instance.to_dict.assert_called_once_with(
            False,
            user=self.user,
            patient=self.patient,
            episode=self.episode
        )

    def test_retrieve_modal(self, fake_pathway_get):
        fake_pathway_get.return_value = self.fake_pathway
        url = reverse("pathway", kwargs=dict(
            name="dog_owner",
            patient_id=self.patient.id,
            episode_id=self.episode.id
        ))

        url = url + "?is_modal=True"
        self.assertTrue(
            self.client.login(
                username=self.user.username, password=self.PASSWORD
            )
        )
        response = self.get_json(url)
        self.assertEqual(response.status_code, 200)
        self.fake_pathway_instance.to_dict.assert_called_once_with(
            True,
            user=self.user,
            episode=self.episode,
            patient=self.patient
        )
