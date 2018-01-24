from opal.core.test import OpalTestCase
from django.core.urlresolvers import reverse


class ReverseUrlTests(OpalTestCase):

    def test_reverse_logout(self):
        self.assertEqual('/accounts/logout/', reverse('logout'))
