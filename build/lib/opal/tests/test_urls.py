from opal.core.test import OpalTestCase
from django.urls import reverse


class ReverseUrlTests(OpalTestCase):

    def test_reverse_logout(self):
        self.assertEqual('/accounts/logout/', reverse('logout'))


    def test_reverse_form_url_with_numbers(self):
        self.assertEqual(
            '/templates/forms/numerical10.html',
            reverse('form_view', kwargs={'model': 'numerical10'})
        )

    def test_reverse_record_url_with_numbers(self):
        self.assertEqual(
            '/templates/record/numerical10.html',
            reverse('record_view', kwargs={'model': 'numerical10'})
        )
