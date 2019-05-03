"""
Unittests for opal.management.commands.create_singletons
"""
from opal.core.test import OpalTestCase
from opal.models import Patient, Episode
from opal.tests.models import EpisodeName, FamousLastWords

from opal.management.commands import create_singletons

class CreateSingletonsTestCase(OpalTestCase):

    def test_handle_create_patient_singleton(self):
        p = Patient.objects.create()
        FamousLastWords.objects.get(patient=p).delete()
        self.assertEqual(0, FamousLastWords.objects.filter(patient=p).count())
        c = create_singletons.Command()
        c.handle()
        self.assertEqual(1, FamousLastWords.objects.filter(patient=p).count())

    def test_handle_create_episode_singleton(self):
        p, e = self.new_patient_and_episode_please()
        EpisodeName.objects.get(episode=e).delete()
        self.assertEqual(0, EpisodeName.objects.filter(episode=e).count())
        c = create_singletons.Command()
        c.handle()
        self.assertEqual(1, EpisodeName.objects.filter(episode=e).count())
