"""
Unittests for opal.models
"""
import datetime

from mock import patch
from django.contrib.auth.models import User
from opal.core.test import OpalTestCase
from opal import models
from opal.models import Subrecord, Tagging, Team, Patient
from opal.tests.models import FamousLastWords, PatientColour

class PatientRecordAccessTestCase(OpalTestCase):

    def test_to_dict(self):
        patient = models.Patient.objects.create()
        access = models.PatientRecordAccess.objects.create(
            user=self.user, patient=patient)
        self.assertEqual(patient.id, access.to_dict(self.user)['patient'])
        self.assertEqual(self.user.username, access.to_dict(self.user)['username'])
        self.assertIsInstance(
            access.to_dict(self.user)['datetime'], datetime.datetime
        )


class PatientTestCase(OpalTestCase):
    def test_bulk_update_patient_subrecords(self):
        original_patient = models.Patient()

        d = {
            "demographics": [{
                "first_name": "Samantha",
                "surname": "Sun",
                "hospital_number": "123312"
            }],
            "patient_colour": [
                {"name": "green"},
                {"name": "purple"},
            ]
        }
        original_patient.bulk_update(d, self.user)

        patient = Patient.objects.get()
        demographics = patient.demographics_set.get()
        self.assertEqual(demographics.first_name, "Samantha")
        self.assertEqual(demographics.surname, "Sun")
        self.assertEqual(demographics.hospital_number, "123312")

        colours = patient.patientcolour_set.all()
        self.assertEqual(len(colours), 2)
        self.assertEqual(colours[0].name, "green")
        self.assertEqual(colours[1].name, "purple")

    def test_bulk_update_without_demographics(self):
        original_patient = models.Patient()

        d = {
            "patient_colour": [
                {"name": "green"},
                {"name": "purple"},
            ]
        }

        with self.assertRaises(ValueError):
            original_patient.bulk_update(d, self.user)

    def test_bulk_update_episode_subrecords_without_episode(self):
        original_patient = models.Patient()

        d = {
            "demographics": [{
                "first_name": "Samantha",
                "surname": "Sun",
                "hospital_number": "123312"
            }],
            "hat_wearer": [
                {"name": "bowler"},
                {"name": "wizard"},
            ]
        }
        self.assertFalse(models.Episode.objects.exists())
        original_patient.bulk_update(d, self.user)

        patient = Patient.objects.get()
        demographics = patient.demographics_set.get()
        self.assertEqual(demographics.first_name, "Samantha")
        self.assertEqual(demographics.surname, "Sun")
        self.assertEqual(demographics.hospital_number, "123312")
        episode = patient.episode_set.get()

        hat_wearers = episode.hatwearer_set.all()
        self.assertEqual(len(hat_wearers), 2)
        self.assertEqual(hat_wearers[0].name, "bowler")
        self.assertEqual(hat_wearers[1].name, "wizard")


class SubrecordTestCase(OpalTestCase):

    @patch('opal.models.find_template')
    def test_display_template(self, find):
        Subrecord.get_display_template()
        find.assert_called_with(['records/subrecord.html'])

    def test_display_template_does_not_exist(self):
        self.assertEqual(None, Subrecord.get_display_template())

    @patch('opal.models.find_template')
    def test_display_template_team(self, find):
        Subrecord.get_display_template(team='test')
        find.assert_called_with([
            'records/test/subrecord.html',
            'records/subrecord.html',
        ])

    @patch('opal.models.find_template')
    def test_display_template_subteam(self, find):
        Subrecord.get_display_template(team='test',
                                       subteam='really')
        find.assert_called_with([
            'records/test/really/subrecord.html',
            'records/test/subrecord.html',
            'records/subrecord.html'
        ])

    @patch('opal.models.find_template')
    def test_detail_template(self, find):
        Subrecord.get_detail_template()
        find.assert_called_with([
            'records/subrecord_detail.html',
            'records/subrecord.html'
        ])

    @patch('opal.models.find_template')
    def test_detail_template_team(self, find):
        Subrecord.get_detail_template(team='test')
        find.assert_called_with([
            'records/subrecord_detail.html',
            'records/subrecord.html'
        ])

    def test_detail_template_does_not_exist(self):
        self.assertEqual(None, Subrecord.get_detail_template())

    @patch('opal.models.find_template')
    def test_detail_template_subteam(self, find):
        Subrecord.get_detail_template(team='test',
                                      subteam='really')
        find.assert_called_with(
            ['records/subrecord_detail.html',
             'records/subrecord.html'])

    @patch('opal.models.find_template')
    def test_form_template(self, find):
        Subrecord.get_form_template()
        find.assert_called_with(['forms/subrecord_form.html'])

    def test_get_modal_template_does_not_exist(self):
        self.assertEqual(None, Subrecord.get_modal_template())

    @patch('opal.models.find_template')
    @patch('opal.models.Subrecord.get_form_template')
    def test_modal_template_no_form_template(self, modal, find):
        modal.return_value = None
        Subrecord.get_modal_template()
        find.assert_called_with(['modals/subrecord_modal.html'])

    @patch('opal.models.find_template')
    def test_modal_template_subteam(self, find):
        Subrecord.get_modal_template(team='test', subteam='really')
        find.assert_called_with([
            'modals/test/really/subrecord_modal.html',
            'modals/test/subrecord_modal.html',
            'modals/subrecord_modal.html',
            'modal_base.html'
        ])


class BulkUpdateFromDictsTest(OpalTestCase):

    def test_bulk_update_from_dict(self):
        self.assertFalse(PatientColour.objects.exists())
        patient_colours = [
            {"name": "purple"},
            {"name": "blue"}
        ]
        patient = Patient.objects.create()
        PatientColour.bulk_update_from_dicts(
            patient, patient_colours, self.user
        )
        expected_patient_colours = set(["purple", "blue"])
        new_patient_colours = set(PatientColour.objects.values_list(
            "name", flat=True
        ))
        self.assertEqual(
            expected_patient_colours, new_patient_colours
        )

    def test_bulk_update_existing_from_dict(self):
        patient = Patient.objects.create()
        patient_colours = []
        for colour in ["green", "red"]:
            patient_colours.append(
                PatientColour.objects.create(patient=patient, name=colour)
            )
        patient_colours = [
            {"name": "purple", "id": patient_colours[0].id},
            {"name": "blue", "id": patient_colours[1].id}
        ]
        PatientColour.bulk_update_from_dicts(
            patient, patient_colours, self.user
        )
        expected_patient_colours = set(["purple", "blue"])
        new_patient_colours = set(PatientColour.objects.values_list(
            "name", flat=True
        ))
        self.assertEqual(
            expected_patient_colours, new_patient_colours
        )

    def test_bulk_update_multiple_singletons_from_dict(self):
        patient = Patient.objects.create()
        famous_last_words = [
            {"words": "so long and thanks for all the fish"},
            {"words": "A towel is the most important item"},
        ]

        with self.assertRaises(ValueError):
            FamousLastWords.bulk_update_from_dicts(
                patient, famous_last_words, self.user
            )


class TaggingImportTestCase(OpalTestCase):
    def test_tagging_import(self):
        import reversion
        from django.db import transaction
        patient = Patient.objects.create()

        with transaction.atomic(), reversion.create_revision():
            team_1 = Team.objects.create(name='team 1', title='team 1')
            team_2 = Team.objects.create(name='team 2', title='team 2')
            mine = Team.objects.create(name='mine', title='mine')
            user_1 = self.user
            user_2 = User.objects.create(
                username="someone",
                is_staff=False,
                is_superuser=False
            )

            # episode 1 has a tag and an archived tag
            episode_1 = patient.create_episode(
                category="testepisode",
            )

            # episode 2 had 1 tag, it was deleted, then it was readded
            episode_2 = patient.create_episode(
                category="testepisode",
            )

            # episode 3 has 2 tags and no new tags
            episode_3 = patient.create_episode(
                category="testepisode",
            )

            # episode 4 has no tags and 2 deleted tags
            episode_4 = patient.create_episode(
                category="testepisode",
            )

            # episode 5 has only user tags, 1 is deleted the other is not
            episode_5 = patient.create_episode(
                category="testepisode",
            )


            # episode 6 has only 1 user tag which has been deleted and replaced
            episode_6 = patient.create_episode(
                category="testepisode",
            )

            # episode 7 has a mixture of both types of user tags and episode tags
            episode_7 = patient.create_episode(
                category="testepisode",
            )

            # episode 1
            Tagging.objects.create(episode=episode_1, team=team_1)
            deleted_tag = Tagging.objects.create(episode=episode_1, team=team_2)

        with transaction.atomic(), reversion.create_revision():
            deleted_tag.delete()

        with transaction.atomic(), reversion.create_revision():
            deleted_tag = Tagging.objects.create(episode=episode_2, team=team_1)

        with transaction.atomic(), reversion.create_revision():
            deleted_tag.delete()

            # episode 2
            Tagging.objects.create(episode=episode_2, team=team_1)

            # episode 3
            Tagging.objects.create(episode=episode_3, team=team_1)
            Tagging.objects.create(episode=episode_3, team=team_2)

            # episode 4
            to_delete_1 = Tagging.objects.create(episode=episode_4, team=team_1)
            to_delete_2 = Tagging.objects.create(episode=episode_4, team=team_2)


        with transaction.atomic(), reversion.create_revision():
            to_delete_1.delete()
            to_delete_2.delete()

        # episode 5
        with transaction.atomic(), reversion.create_revision():
            Tagging.objects.create(episode=episode_5, team=mine, user=user_1)
            to_delete = Tagging.objects.create(episode=episode_5, team=mine, user=user_2)

        with transaction.atomic(), reversion.create_revision():
            to_delete.delete()

        # episode 6
        with transaction.atomic(), reversion.create_revision():
            to_delete = Tagging.objects.create(episode=episode_6, team=mine, user=user_1)

        with transaction.atomic(), reversion.create_revision():
            to_delete.delete()

        with transaction.atomic(), reversion.create_revision():
            Tagging.objects.create(episode=episode_6, team=mine, user=user_1)

        # episode 7
        with transaction.atomic(), reversion.create_revision():
            Tagging.objects.create(episode=episode_7, team=mine, user=user_1)
            to_delete_1 = Tagging.objects.create(episode=episode_7, team=mine, user=user_2)

            Tagging.objects.create(episode=episode_7, team=team_1)
            to_delete_2 = Tagging.objects.create(episode=episode_7, team=team_2)

        with transaction.atomic(), reversion.create_revision():
            to_delete_1.delete()
            to_delete_2.delete()

        Tagging.import_from_reversion()

        self.assertTrue(Tagging.objects.filter(
            episode=episode_1, team=team_1, archived=False
            ).exists()
        )
        self.assertTrue(Tagging.objects.filter(
            episode=episode_1, team=team_2, archived=True
            ).exists()
        )
        self.assertEqual(Tagging.objects.filter(episode=episode_1).count(), 2)

        self.assertTrue(Tagging.objects.filter(
            episode=episode_2, team=team_1, archived=False
            ).exists()
        )
        self.assertEqual(Tagging.objects.filter(episode=episode_2).count(), 1)

        self.assertTrue(Tagging.objects.filter(
            episode=episode_3, team=team_1, archived=False
            ).exists()
        )
        self.assertTrue(Tagging.objects.filter(
            episode=episode_3, team=team_2, archived=False
            ).exists()
        )
        self.assertEqual(Tagging.objects.filter(episode=episode_1).count(), 2)

        self.assertTrue(Tagging.objects.filter(
            episode=episode_4, team=team_1, archived=True
            ).exists()
        )
        self.assertTrue(Tagging.objects.filter(
            episode=episode_4, team=team_2, archived=True
            ).exists()
        )
        self.assertEqual(Tagging.objects.filter(episode=episode_1).count(), 2)

        self.assertTrue(Tagging.objects.filter(
            episode=episode_5, team=mine, user=user_1, archived=False
            ).exists()
        )
        self.assertTrue(Tagging.objects.filter(
            episode=episode_5, team=mine, user=user_2, archived=True
            ).exists()
        )
        self.assertEqual(Tagging.objects.filter(episode=episode_5).count(), 2)

        self.assertTrue(Tagging.objects.filter(
            episode=episode_6, team=mine, user=user_1, archived=False
            ).exists()
        )
        self.assertEqual(Tagging.objects.filter(episode=episode_6).count(), 1)

        self.assertTrue(Tagging.objects.filter(
            episode=episode_7, team=mine, user=user_1, archived=False
            ).exists()
        )
        self.assertTrue(Tagging.objects.filter(
            episode=episode_7, team=mine, user=user_2, archived=True
            ).exists()
        )
        self.assertTrue(Tagging.objects.filter(
            episode=episode_7, team=team_1, archived=False
            ).exists()
        )
        self.assertTrue(Tagging.objects.filter(
            episode=episode_7, team=team_2, archived=True
            ).exists()
        )
        self.assertEqual(Tagging.objects.filter(episode=episode_7).count(), 4)
