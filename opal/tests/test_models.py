"""
Unittests for opal.models
"""
import datetime
from mock import patch, MagicMock

from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

from opal import models
from opal.core import exceptions
from opal.models import Subrecord, Tagging, Team, Patient, InpatientAdmission
from opal.core.test import OpalTestCase
import opal.tests.test_patient_lists # To make sure test tagged lists are pulled in
from opal.tests.models import FamousLastWords, PatientColour, ExternalSubRecord

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

    def test_create_episode_category(self):
        patient = models.Patient.objects.create()
        e = patient.create_episode(category='testcategory')
        self.assertEqual('testcategory', e.category)

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
        self.assertTrue(patient.episode_set.exists())

    def test_bulk_update_with_existing_patient_episode(self):
        original_patient = models.Patient()
        original_patient.save()
        original_episode = original_patient.create_episode()

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
        self.assertTrue(patient.episode_set.get(), original_episode)

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
            ],
            "location": [
                {
                    "ward": "a ward",
                    "bed": "a bed"
                },
            ]
        }
        self.assertFalse(models.Episode.objects.exists())
        original_patient.bulk_update(d, self.user)

        patient = Patient.objects.get()
        demographics = patient.demographics_set.get()
        self.assertEqual(demographics.first_name, "Samantha")
        self.assertEqual(demographics.surname, "Sun")
        self.assertEqual(demographics.hospital_number, "123312")
        self.assertEqual(models.Episode.objects.count(), 1)
        episode = patient.episode_set.get()

        hat_wearers = episode.hatwearer_set.all()
        self.assertEqual(len(hat_wearers), 2)
        self.assertEqual(hat_wearers[0].name, "bowler")
        self.assertEqual(hat_wearers[1].name, "wizard")
        self.assertEqual(hat_wearers[0].episode, episode)
        self.assertEqual(hat_wearers[1].episode, episode)

        location = episode.location_set.get()
        self.assertEqual(location.bed, "a bed")
        self.assertEqual(location.ward, "a ward")


class SubrecordTestCase(OpalTestCase):

    def test_display_template_does_not_exist(self):
        self.assertEqual(None, Subrecord.get_display_template())

    @patch('opal.models.find_template')
    def test_display_template(self, find):
        Subrecord.get_display_template()
        find.assert_called_with(['records/subrecord.html'])

    @patch('opal.models.find_template')
    def test_display_template_list(self, find):
        patient_list = MagicMock()
        patient_list.get_template_prefixes = MagicMock(return_value=["test"])
        Subrecord.get_display_template(patient_list=patient_list)
        find.assert_called_with([
            'records/test/subrecord.html',
            'records/subrecord.html',
        ])

    @patch('opal.models.find_template')
    def test_display_template_episode_type(self, find):
        Subrecord.get_display_template(episode_type='Inpatient')
        find.assert_called_with([
            'records/inpatient/subrecord.html',
            'records/subrecord.html',
        ])

    @patch('opal.models.find_template')
    def test_display_template_list_episode_type(self, find):
        with self.assertRaises(ValueError):
            Subrecord.get_display_template(
                patient_list='test', episode_type='Inpatient'
            )

    def test_detail_template_does_not_exist(self):
        self.assertEqual(None, Subrecord.get_detail_template())

    @patch('opal.models.find_template')
    def test_detail_template(self, find):
        Subrecord.get_detail_template()
        find.assert_called_with([
            'records/subrecord_detail.html',
            'records/subrecord.html'
        ])

    @patch('opal.models.find_template')
    def test_detail_template_list(self, find):
        Subrecord.get_detail_template(patient_list='test')
        find.assert_called_with([
            'records/subrecord_detail.html',
            'records/subrecord.html'
        ])

    @patch('opal.models.find_template')
    def test_detail_template_episode_type(self, find):
        Subrecord.get_detail_template(episode_type='Inpatient')
        find.assert_called_with([
            'records/inpatient/subrecord_detail.html',
            'records/inpatient/subrecord.html',
            'records/subrecord_detail.html',
            'records/subrecord.html'
        ])

    @patch('opal.models.find_template')
    def test_detail_template_list_episode_type(self, find):
        with self.assertRaises(ValueError):
            Subrecord.get_detail_template(episode_type='Inpatient', patient_list='test')

    def test_form_template_does_not_exist(self):
        self.assertEqual(None, Subrecord.get_form_template())

    @patch('opal.models.find_template')
    def test_form_template(self, find):
        Subrecord.get_form_template()
        find.assert_called_with(['forms/subrecord_form.html'])

    @patch('opal.models.find_template')
    def test_form_template_list(self, find):
        patient_list = MagicMock()
        patient_list.get_template_prefixes = MagicMock(return_value=["test"])
        Subrecord.get_form_template(patient_list=patient_list)
        find.assert_called_with([
            'forms/test/subrecord_form.html',
            'forms/subrecord_form.html'
        ])

    @patch('opal.models.find_template')
    def test_form_template_episode_type(self, find):
        Subrecord.get_form_template(episode_type='Inpatient')
        find.assert_called_with([
            'forms/inpatient/subrecord_form.html',
            'forms/subrecord_form.html'
        ])

    @patch('opal.models.find_template')
    def test_form_template_list_episode_type(self, find):
        with self.assertRaises(ValueError):
            Subrecord.get_form_template(episode_type='Inpatient', patient_list='test')

    def test_get_modal_template_does_not_exist(self):
        self.assertEqual(None, Subrecord.get_modal_template())

    @patch('opal.models.find_template')
    @patch('opal.models.Subrecord.get_form_template')
    def test_modal_template_no_form_template(self, modal, find):
        modal.return_value = None
        Subrecord.get_modal_template()
        find.assert_called_with(['modals/subrecord_modal.html'])

    @patch('opal.models.find_template')
    def test_modal_template_list(self, find):
        patient_list = MagicMock()
        patient_list.get_template_prefixes = MagicMock(return_value=["test"])
        Subrecord.get_modal_template(patient_list=patient_list)
        find.assert_called_with([
            'modals/test/subrecord_modal.html',
            'modals/subrecord_modal.html',
            'modal_base.html'
        ])

    @patch('opal.models.find_template')
    def test_modal_template_episode_type(self, find):
        Subrecord.get_modal_template(episode_type='Inpatient')
        find.assert_called_with([
            'modals/inpatient/subrecord_modal.html',
            'modals/subrecord_modal.html',
            'modal_base.html'
        ])

    @patch('opal.models.find_template')
    def test_modal_template_episode_type_list(self, find):
        with self.assertRaises(ValueError):
            Subrecord.get_modal_template(episode_type='Inpatient', patient_list='test')


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

    def test_bulk_update_singleton(self):
        patient = Patient.objects.create()
        famous_model = FamousLastWords.objects.get()
        famous_model.set_consistency_token()
        famous_model.save()

        famous_last_words = [
            {"words": "A towel is the most important item"},
        ]

        with self.assertRaises(exceptions.APIError):
            FamousLastWords.bulk_update_from_dicts(
                patient, famous_last_words, self.user
            )

    def test_bulk_update_singleton_with_force(self):
        patient = Patient.objects.create()
        famous_model = FamousLastWords.objects.get()
        famous_model.set_consistency_token()
        famous_model.save()

        famous_last_words = [
            {"words": "A towel is the most important item"},
        ]

        FamousLastWords.bulk_update_from_dicts(
            patient, famous_last_words, self.user, force=True
        )

        result = FamousLastWords.objects.get()
        self.assertEqual(result.words, famous_last_words[0].values()[0])


class InpatientAdmissionTestCase(OpalTestCase):
    def test_updates_with_external_identifer(self):
        patient = models.Patient()
        patient.save()
        yesterday = timezone.make_aware(datetime.datetime.now() - datetime.timedelta(1))
        InpatientAdmission.objects.create(
            datetime_of_admission=yesterday,
            external_identifier="1",
            patient=patient
        )

        now = timezone.make_aware(datetime.datetime.now()).strftime(
            settings.DATETIME_INPUT_FORMATS[0]
        )

        update_dict = dict(
            datetime_of_admission=now,
            external_identifier="1",
            patient_id=patient.id
        )

        a = InpatientAdmission()
        a.update_from_dict(update_dict, self.user)

        result = InpatientAdmission.objects.get()
        self.assertEqual(
            result.datetime_of_admission.date(),
            datetime.date.today()
        )

    def test_no_external_identifier(self):
        patient = models.Patient()
        patient.save()
        yesterday = timezone.make_aware(datetime.datetime.now() - datetime.timedelta(1))
        InpatientAdmission.objects.create(
            datetime_of_admission=yesterday,
            external_identifier="1",
            patient=patient
        )

        now = datetime.datetime.now().strftime(
            settings.DATETIME_INPUT_FORMATS[0]
        )

        update_dict = dict(
            datetime_of_admission=now,
            patient_id=patient.id
        )

        a = InpatientAdmission()
        a.update_from_dict(update_dict, self.user)

        results = InpatientAdmission.objects.all()
        self.assertEqual(2, len(results))

        self.assertEqual(
            results[0].datetime_of_admission.date(),
            yesterday.date()
        )

        self.assertEqual(
            results[1].datetime_of_admission.date(),
            datetime.date.today()
        )

    def test_doesnt_update_empty_external_identifier(self):
        patient = models.Patient()
        patient.save()
        yesterday = timezone.make_aware(datetime.datetime.now() - datetime.timedelta(1))
        InpatientAdmission.objects.create(
            datetime_of_admission=yesterday,
            external_identifier="",
            patient=patient
        )

        now = datetime.datetime.now().strftime(
            settings.DATETIME_INPUT_FORMATS[0]
        )

        update_dict = dict(
            datetime_of_admission=now,
            external_identifier="",
            patient_id=patient.id
        )

        a = InpatientAdmission()
        a.update_from_dict(update_dict, self.user)

        results = InpatientAdmission.objects.all()
        self.assertEqual(2, len(results))

        self.assertEqual(
            results[0].datetime_of_admission.date(),
            yesterday.date()
        )

        self.assertEqual(
            results[1].datetime_of_admission.date(),
            datetime.date.today()
        )

    def test_doesnt_update_a_different_patient(self):
        other_patient = Patient.objects.create()
        patient = models.Patient()
        patient.save()
        yesterday = timezone.make_aware(datetime.datetime.now() - datetime.timedelta(1))
        InpatientAdmission.objects.create(
            datetime_of_admission=yesterday,
            external_identifier="1",
            patient=patient
        )

        now = datetime.datetime.now().strftime(
            settings.DATETIME_INPUT_FORMATS[0]
        )

        update_dict = dict(
            datetime_of_admission=now,
            external_identifier="",
            patient_id=other_patient.id
        )

        a = InpatientAdmission()
        a.update_from_dict(update_dict, self.user)

        results = InpatientAdmission.objects.all()
        self.assertEqual(2, len(results))

        self.assertEqual(
            results[0].datetime_of_admission.date(),
            yesterday.date()
        )

        self.assertEqual(
            results[1].datetime_of_admission.date(),
            datetime.date.today()
        )


class TaggingTestCase(OpalTestCase):
    def test_display_template(self):
        self.assertEqual('tagging.html', Tagging.get_display_template())

    def test_form_template(self):
        self.assertEqual('tagging_modal.html', Tagging.get_form_template())

    def test_field_schema(self):
        names = ['eater', 'herbivore', 'carnivore']
        fields = [{'name': tagname, 'type': 'boolean'} for tagname in names]
        schema = Tagging.build_field_schema()
        for field in fields:
            self.assertIn(field, schema)


class TaggingImportTestCase(OpalTestCase):

    def test_tagging_import_from_reversion(self):
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


class AbstractDemographicsTestCase(OpalTestCase):
    def test_name(self):
        d = models.Demographics(first_name='Jane',
                                surname='Doe',
                                middle_name='Obsidian')
        self.assertEqual('Jane Doe', d.name)


class ExternalSystemTestCase(OpalTestCase):
    def test_get_footer(self):
        self.assertEqual(
            ExternalSubRecord.get_modal_footer_template(),
            "partials/_sourced_modal_footer.html"
        )
