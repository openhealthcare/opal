"""
Unittests for opal.management.commands.create_singletons
"""
from unittest import mock
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
        with mock.patch.object(c.style, "SUCCESS") as success:
            with mock.patch.object(c.stdout, "write") as stdout_write:
                success.side_effect = lambda x: x
                c.handle()
        self.assertEqual(1, FamousLastWords.objects.filter(patient=p).count())
        stdout_write.assert_called_once_with("Created singletons: 1 FamousLastWords")

    def test_handle_create_episode_singleton(self):
        p, e = self.new_patient_and_episode_please()
        EpisodeName.objects.get(episode=e).delete()
        self.assertEqual(0, EpisodeName.objects.filter(episode=e).count())
        c = create_singletons.Command()
        with mock.patch.object(c.style, "SUCCESS") as success:
            with mock.patch.object(c.stdout, "write") as stdout_write:
                success.side_effect = lambda x: x
                c.handle()
        self.assertEqual(1, EpisodeName.objects.filter(episode=e).count())
        stdout_write.assert_called_once_with("Created singletons: 1 EpisodeName")

    def test_handle_with_none(self):
        c = create_singletons.Command()
        with mock.patch.object(c.stdout, "write") as stdout_write:
            c.handle()
        stdout_write.assert_called_once_with("No singletons needed to be created")
