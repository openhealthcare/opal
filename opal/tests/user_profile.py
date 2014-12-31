"""
Tests for opal.models.UserProfile
"""
from django.test import TestCase

from django.contrib.auth.models import User

from opal.models import UserProfile, Team

class UserProfileTest(TestCase):

    def setUp(self):
        self.user = User(username='testing')
        self.user.save()
        self.profile, _ = UserProfile.objects.get_or_create(user=self.user)

    def test_get_roles(self):
        self.assertEqual({'default': []}, self.profile.get_roles())

    def test_get_teams(self):
        teams = list(Team.objects.filter(active=True, restricted=False))
        user_teams = self.profile.get_teams()
        for t in teams:
            self.assertIn(t, user_teams) 
