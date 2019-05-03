from opal.core.test import OpalTestCase
from django.urls import reverse
from opal.core.pathway.tests.pathway_test import pathways as test_pathways


class PathwayIndexViewTestCase(OpalTestCase):
    def test_logged_in_get_index_view(self):
        url = reverse("pathway_index")
        self.client.login(
            username=self.user.username, password=self.PASSWORD
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pathway/index.html')

    def test_not_logged_in_get_index_view(self):
        url = reverse("pathway_index")
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')


class PathwayTemplateViewTestCase(OpalTestCase):
    def get_response(self, pathway, login=True, is_modal=False):
        url = reverse("pathway_template", kwargs=dict(name=pathway.slug))
        if is_modal:
            url = url + "?is_modal=True"
        if login:
            self.client.login(
                username=self.user.username, password=self.PASSWORD
            )
        return self.client.get(url)

    def test_integration_page_modal(self):
        response = self.get_response(
            test_pathways.PagePathwayExample(), is_modal=True
        )
        self.assertEqual(response.status_code, 200)
        content = str(response.content)
        self.assertIn("modal-body", content)
        self.assertIn('form name="form"', content)

        # make sure the icon is rendered
        self.assertIn('fa fa-something', content)

    def test_integration_page_non_modal(self):
        response = self.get_response(
            test_pathways.PagePathwayExample(), is_modal=False
        )
        self.assertEqual(response.status_code, 200)
        content = str(response.content)
        self.assertNotIn("modal-body", content)
        self.assertIn('form name="form"', content)

        # make sure the icon is rendered
        self.assertIn('fa fa-something', content)

    def test_integration_wizard_modal(self):
        response = self.get_response(
            test_pathways.WizardPathwayExample(), is_modal=True
        )
        self.assertEqual(response.status_code, 200)
        content = str(response.content)
        self.assertIn("modal-body", content)
        self.assertIn('form name="form"', content)

        # make sure the icon is rendered
        self.assertIn('fa fa-something', content)

    def test_integration_wizard_non_modal(self):
        response = self.get_response(
            test_pathways.WizardPathwayExample(), is_modal=False
        )

        self.assertEqual(response.status_code, 200)
        content = str(response.content)
        self.assertNotIn("modal-body", content)
        self.assertIn('form name="form"', content)

        # make sure the icon is rendere
        self.assertIn('fa fa-something', content)

    def test_login_required(self):
        response = self.get_response(
            test_pathways.WizardPathwayExample(), login=False
        )
        self.assertEqual(response.status_code, 302)

    def test_step_rendered(self):
        """
            Make sure Step display name and icon
            are rendered in the pathway templates
        """
        pathway_types = [
            test_pathways.WizardPathwayExample,
            test_pathways.PagePathwayExample
        ]
        for pathway in pathway_types:
            for is_modal in [True, False]:
                response = self.get_response(
                    pathway(), is_modal=is_modal
                )

            self.assertEqual(response.status_code, 200)
            self.assertIn("Colour", str(response.content))
            self.assertIn('fa fa-something', str(response.content))
