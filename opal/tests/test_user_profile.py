"""
Tests for opal.models.UserProfile
"""
from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch

from opal.models import UserProfile

GRAVATAR  = 'http://gravatar.com/avatar/55502f40dc8b7c769880b10874abc9d0?s=80&r=g&d=identicon'
GRAVATAR2 = 'http://gravatar.com/avatar/ae2b1fca515949e5d54fb22b8ed95575?s=80&r=g&d=identicon'

class UserProfileTest(TestCase):

    def setUp(self):
        self.user = User(
            username='testing',
            first_name='Test', last_name='User'
        )
        self.user.save()
        self.profile = self.user.profile

    def test_to_dict_has_full_name(self):
        as_dict = self.profile.to_dict()
        self.assertEqual('Test User', as_dict['full_name'])

    def test_to_dict_has_avatar_url(self):
        as_dict = self.profile.to_dict()
        self.assertTrue('avatar_url' in as_dict)

    def test_to_dict_has_id(self):
        self.assertEqual(self.user.id, self.profile.to_dict()['user_id'])

    def test_get_avatar_url(self):
        self.profile.user.email = 'test@example.com'
        self.profile.user.save()
        url = self.profile.get_avatar_url()
        self.assertEqual(url, GRAVATAR)

    def test_get_avatar_url_uppercase_in_email(self):
        self.profile.user.email = 'TEST@example.com'
        self.profile.user.save()
        url = self.profile.get_avatar_url()
        self.assertEqual(url, GRAVATAR)

    def test_get_avatar_url_uses_username_if_no_email(self):
        url = self.profile.get_avatar_url()
        self.assertEqual(url, GRAVATAR2)

    def test_get_roles(self):
        self.assertEqual({'default': []}, self.profile.get_roles())

    def test_explicit_access_only(self):
        with patch.object(UserProfile, 'get_roles') as mock_roles:
            mock_roles.return_value = dict(default=['scientist'])
            self.assertEqual(True, self.profile.explicit_access_only)
