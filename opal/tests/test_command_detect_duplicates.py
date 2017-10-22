"""
Unittests for opal.management.commands.detect_duplicates
"""
from __future__ import unicode_literals

import datetime

from mock import patch

from opal.core.test import OpalTestCase
from opal import models

from opal.management.commands import detect_duplicates as detector

class CommandTestCase(OpalTestCase):

    def test_handle(self):
        patient = models.Patient.objects.create()
        c = detector.Command()
        with patch.object(c.stdout, 'write') as writer:
            c.handle()
            writer.assert_any_call('Duplicate detection starting...')

    def test_handle_duplicate_names(self):
        p1 = models.Patient.objects.create()
        d1 = p1.demographics_set.get()
        d1.first_name = 'Jenny'
        d1.surname = 'Smith'
        d1.save()

        p2 = models.Patient.objects.create()
        d2 = p2.demographics_set.get()
        d2.first_name = 'Jenny'
        d2.surname = 'Smith'
        d2.save()

        c = detector.Command()
        with patch.object(c.stdout, 'write') as writer:
            c.handle()

            writer.assert_any_call('Jenny Smith {0}'.format(p1.id))
            writer.assert_any_call('Jenny Smith {0}'.format(p2.id))


    def test_handle_duplicate_with_three(self):
        """
        Print the duplicate triple once, but not the third instance.
        """
        p1 = models.Patient.objects.create()
        d1 = p1.demographics_set.get()
        d1.first_name = 'Jenny'
        d1.surname = 'Smith'
        d1.save()

        p2 = models.Patient.objects.create()
        d2 = p2.demographics_set.get()
        d2.first_name = 'Jenny'
        d2.surname = 'Smith'
        d2.save()

        p3 = models.Patient.objects.create()
        d3 = p3.demographics_set.get()
        d3.first_name = 'Jenny'
        d3.surname = 'Smith'
        d3.save()

        c = detector.Command()
        with patch.object(c.stdout, 'write') as writer:
            c.handle()

            writer.assert_any_call('Jenny Smith {0}'.format(p1.id))
            writer.assert_any_call('Jenny Smith {0}'.format(p2.id))
            with self.assertRaises(AssertionError):
                writer.assert_any_call('Jenny Smith {0}'.format(p3.id))

    def test_handle_duplicate_dobs(self):
        p1 = models.Patient.objects.create()
        d1 = p1.demographics_set.get()
        d1.first_name = 'Jenny'
        d1.surname = 'Smiths'
        d1.date_of_birth = datetime.date(1934, 2, 2)
        d1.save()

        p2 = models.Patient.objects.create()
        d2 = p2.demographics_set.get()
        d2.first_name = 'Jenny'
        d2.surname = 'Smith'
        d2.date_of_birth = datetime.date(1934, 2, 2)
        d2.save()

        c = detector.Command()
        with patch.object(c.stdout, 'write') as writer:
            c.handle()

            writer.assert_any_call('Jenny Smiths {0}'.format(p1.id))
            writer.assert_any_call('Jenny Smith {0}'.format(p2.id))
