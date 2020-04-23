"""
Unittests to check that the signals defined in
opal.core.signals.worker are called at the appropriate
times and with the appropriate signature.
"""
from unittest.mock import MagicMock
from django.dispatch import receiver

from opal.core.test import OpalTestCase
from opal.models import Patient
from opal.tests.models import Colour

from opal.core.signals import worker

class PatientPostSaveTestCase(OpalTestCase):

    def test_sender(self):
        mock_receiver = MagicMock(name='mock receiver')
        worker.patient_post_save.connect(mock_receiver)
        p = Patient.objects.create()
        self.assertEqual(1, mock_receiver.call_count)
        args, kwargs = mock_receiver.call_args
        self.assertEqual(p, kwargs['instance'])

class EpisodePostSaveTestCase(OpalTestCase):
    def test_sender(self):
        mock_receiver = MagicMock(name='mock receiver')
        worker.episode_post_save.connect(mock_receiver)
        p = Patient.objects.create()
        episode = p.create_episode()
        self.assertEqual(1, mock_receiver.call_count)
        args, kwargs = mock_receiver.call_args
        self.assertEqual(episode, kwargs['instance'])

class SubrecordPostSaveTestCase(OpalTestCase):
    def test_sender(self):
        mock_receiver = MagicMock(name='mock receiver')

        @receiver(worker.subrecord_post_save, sender=Colour)
        def rec(*a, **k):
            mock_receiver(*a, **k)

        p, e = self.new_patient_and_episode_please()
        blue = Colour(episode=e, name='Blue')
        blue.save()


        self.assertEqual(1, mock_receiver.call_count)
