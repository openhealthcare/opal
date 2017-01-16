"""
Tests for opal.models.UserProfile
"""
from django.contrib.auth.models import User
from django.test import TestCase
from mock import patch

from opal.models import UserProfile

class UserProfileTest(TestCase):

    def setUp(self):
        self.user = User(username='testing')
        self.user.save()
        self.profile, _ = UserProfile.objects.get_or_create(user=self.user)

    def test_get_roles(self):
        self.assertEqual({'default': []}, self.profile.get_roles())

    def test_can_see_pid(self):
        with patch.object(UserProfile, 'get_roles') as mock_roles:
            mock_roles.return_value = dict(default=['scientist'])
            self.assertEqual(False, self.profile.can_see_pid)

    def test_explicit_access_only(self):
        with patch.object(UserProfile, 'get_roles') as mock_roles:
            mock_roles.return_value = dict(default=['scientist'])
            self.assertEqual(True, self.profile.explicit_access_only)
