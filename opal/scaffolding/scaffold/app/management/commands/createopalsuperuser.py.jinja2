from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from opal.models import UserProfile

class Command(BaseCommand):
    @transaction.atomic()
    def handle(self, *args, **options):
        user = User(username='super')
        user.set_password('super1')
        user.is_superuser = True
        user.is_staff = True
        user.save()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.force_password_change = False
        profile.save()
