"""
Unittests for opal.models
"""
import os
import datetime
from unittest.mock import patch

from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User

from opal import models
from opal.core import application, exceptions, subrecords
from opal.models import (
    Subrecord, Tagging, Patient, InpatientAdmission, Symptom,
)
from opal.core.test import OpalTestCase
from opal.core import patient_lists
from opal.tests import test_patient_lists
from opal.tests.models import (
    FamousLastWords, PatientColour, ExternalSubRecord, SymptomComplex,
    PatientConsultation, Birthday, DogOwner, HatWearer, InvisibleHatWearer,
    HouseOwner, HoundOwner, Colour, FavouriteColour, Dinner,
    EntitledHatWearer
)


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

    def test_get_absolute_url(self):
        patient = models.Patient.objects.create()
        expected = '/#/patient/{}'.format(patient.id)
        self.assertEqual(expected, patient.get_absolute_url())

    def test_demographics(self):
        patient = models.Patient.objects.create()
        self.assertEqual(patient.demographics_set.get(), patient.demographics())

    def test_demographics_does_not_exist(self):
        # This is one of those things that should not exist, but let's make
        # doubly sure that we raise an exception if it does happen !
        patient = models.Patient.objects.create()
        patient.demographics_set.get().delete()
        Demographics = subrecords.get_subrecord_from_model_name('Demographics')
        with self.assertRaises(Demographics.DoesNotExist):
            demographics = patient.demographics()

    def test_create_episode(self):
        patient = models.Patient()
        patient.save()
        episode = patient.create_episode()
        self.assertEqual(models.Episode, episode.__class__)
        self.assertEqual(patient, episode.patient)

    def test_to_dict_episode_identical_to_episode_to_dict(self):
        patient, episode = self.new_patient_and_episode_please()
        episode_dict = episode.to_dict(self.user)
        self.assertEqual(episode_dict, patient.to_dict(self.user)['episodes'][episode.id])

    def test_created_with_the_default_episode(self):
        _, episode = self.new_patient_and_episode_please()
        self.assertEqual(
            application.get_app().default_episode_category,
            episode.category_name
        )

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
        demographics = patient.demographics()
        self.assertEqual(demographics.first_name, "Samantha")
        self.assertEqual(demographics.surname, "Sun")
        self.assertEqual(demographics.hospital_number, "123312")

        colours = patient.patientcolour_set.all()
        self.assertEqual(len(colours), 2)
        self.assertTrue(patient.episode_set.exists())

    def test_bulk_update_patient_subrecords_respects_order(self):
        patient = models.Patient()

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
        patient.bulk_update(d, self.user)
        colours = patient.patientcolour_set.all()
        expected = set(["green", "purple"])
        found = set([colours[0].name, colours[1].name])
        self.assertEqual(expected, found)

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
        demographics = patient.demographics()
        self.assertEqual(demographics.first_name, "Samantha")
        self.assertEqual(demographics.surname, "Sun")
        self.assertEqual(demographics.hospital_number, "123312")

        colours = patient.patientcolour_set.all()
        self.assertEqual(len(colours), 2)
        self.assertEqual(
            set([colours[0].name, colours[1].name]),
            set(["green", "purple"]),
        )
        self.assertTrue(patient.episode_set.get(), original_episode)

    def test_bulk_update_without_demographics(self):
        original_patient = models.Patient()

        d = {
            "patient_colour": [
                {"name": "green"},
                {"name": "purple"},
            ]
        }

        original_patient.bulk_update(d, self.user)
        self.assertEqual(
            original_patient.demographics().hospital_number, ""
        )

    def test_bulk_update_tagging(self):
        original_patient = models.Patient()
        original_patient.save()

        d = {
            "demographics": [{
                "first_name": "Samantha",
                "surname": "Sun",
                "hospital_number": "123312"
            }],
            "tagging": [
                {"id": 1, 'inpatient': True},
            ]
        }
        original_patient.bulk_update(d, self.user)
        episode = original_patient.episode_set.first()
        self.assertEqual(['inpatient'], episode.get_tag_names(self.user))

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
        demographics = patient.demographics()
        self.assertEqual(demographics.first_name, "Samantha")
        self.assertEqual(demographics.surname, "Sun")
        self.assertEqual(demographics.hospital_number, "123312")
        self.assertEqual(models.Episode.objects.count(), 1)
        episode = patient.episode_set.get()

        hat_wearers = episode.hatwearer_set.all()
        self.assertEqual(len(hat_wearers), 2)
        expected = set(["bowler", "wizard"])
        found = set([hat_wearers[0].name, hat_wearers[1].name])
        self.assertEqual(
            expected, found
        )
        self.assertEqual(hat_wearers[0].episode, episode)
        self.assertEqual(hat_wearers[1].episode, episode)

        location = episode.location_set.get()
        self.assertEqual(location.bed, "a bed")
        self.assertEqual(location.ward, "a ward")

    def test_bulk_update_create_new_episode_for_preexisting_patient_if_not_passed_explicitly(self):
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
        original_patient.save()
        original_patient.create_episode()
        self.assertEqual(1, original_patient.episode_set.count())
        original_patient.bulk_update(d, self.user)
        self.assertEqual(2, original_patient.episode_set.count())
        self.assertEqual(models.Episode.objects.count(), 2)
        location = original_patient.episode_set.last().location_set.first()
        self.assertEqual(location.ward, "a ward")


class SubrecordTestCase(OpalTestCase):

    @patch('opal.models.find_template')
    def test_get_template(self, find):
        find.return_value = "found"
        result = Subrecord._get_template("a_{}_b")
        find.assert_called_once_with(["a_subrecord_b"])
        self.assertEqual(result, "found")

    @patch('opal.models.find_template')
    def test_get_template_with_prefixes(self, find):
        find.return_value = "found"
        result = Subrecord._get_template("a_{}_b", prefixes=["onions"])

        find.assert_called_once_with([
            os.path.join("a_onions", "subrecord_b"),
            "a_subrecord_b"
        ])
        self.assertEqual(result, "found")

    def test_get_display_name_from_meta_verbose_name(self):
        self.assertEqual(
            'Invisible Wearer of Hats',
            InvisibleHatWearer.get_display_name()
        )

    def test_get_display_name_from_verbose_name_but_capwords(self):
        self.assertEqual(
            'Dog Owner',
            DogOwner.get_display_name()
        )

    def test_date_time_deserialisation(self):
        patient, _ = self.new_patient_and_episode_please()
        birthday_date = "10/1/2000"
        birthday_party = "11/2/2016 20:30:10"
        birthday = Birthday()
        birthday.update_from_dict(dict(
            birth_date=birthday_date,
            party=birthday_party,
            patient_id=patient.id
        ), self.user)

        bday = Birthday.objects.get()
        self.assertEqual(bday.patient_id, patient.id)
        self.assertEqual(bday.birth_date, datetime.date(2000, 1, 10))
        # stip off miliseconds, we don't use them
        start = bday.party.isoformat()[:19]
        expected_start = '2016-02-11T20:30:10'
        self.assertEqual(start, expected_start)

    def test_display_template_does_not_exist(self):
        self.assertEqual(None, Subrecord.get_display_template())

    def test_time_deserialisation(self):
        _, episode = self.new_patient_and_episode_please()
        dinner_time = "20:00:00"
        dinner = Dinner()
        dinner.update_from_dict(dict(
            episode_id=episode.id,
            time=dinner_time
        ), self.user)

        reloaded = Dinner.objects.get()
        self.assertEqual(
            reloaded.time, datetime.time(20)
        )

    def test_time_serialisation(self):
        _, episode = self.new_patient_and_episode_please()
        dinner = episode.dinner_set.create(time=datetime.time(20))
        result = dinner.to_dict(self.user)
        self.assertEqual(
            result["time"], datetime.time(20, 0)
        )

    @patch('opal.models.find_template')
    def test_display_template(self, find):
        Subrecord.get_display_template()
        find.assert_called_with([os.path.join('records', 'subrecord.html')])

    def test_detail_template_does_not_exist(self):
        self.assertEqual(None, Subrecord.get_detail_template())

    @patch('opal.models.find_template')
    def test_detail_template(self, find):
        Subrecord.get_detail_template()
        find.assert_called_with([
            os.path.join('records', 'subrecord_detail.html'),
            os.path.join('records', 'subrecord.html'),
        ])

    @patch('opal.models.find_template')
    def test_detail_template_prefixes(self, find):
        find.return_value = None
        Subrecord.get_detail_template(prefixes=['onions'])
        self.assertEqual(
            find.call_args_list[0][0][0],
            [
                os.path.join('records', 'onions', 'subrecord_detail.html'),
                os.path.join('records', 'onions', 'subrecord.html'),
                os.path.join('records', 'subrecord_detail.html'),
                os.path.join('records', 'subrecord.html'),
            ]
        )

    def test_form_template_does_not_exist(self):
        self.assertEqual(None, Subrecord.get_form_template())

    @patch('opal.models.find_template')
    def test_form_template(self, find):
        Subrecord.get_form_template()
        find.assert_called_with([os.path.join('forms', 'subrecord_form.html')])

    def test_get_form_url(self):
        url = Subrecord.get_form_url()
        self.assertEqual(url, '/templates/forms/subrecord.html')

    @patch('opal.models.find_template')
    def test_form_template_prefixes(self, find):
        Subrecord.get_form_template(prefixes=['onions'])
        find.assert_called_with([
            os.path.join('forms', 'onions', 'subrecord_form.html'),
            os.path.join('forms', 'subrecord_form.html'),
        ])

    @patch('opal.models.find_template')
    @patch('opal.models.Subrecord.get_form_template')
    @patch('opal.models.Subrecord._get_template')
    def test_modal_template(self, get_template, get_form_template, find):
        get_form_template.return_value = "some_template"
        get_template.return_value = None
        Subrecord.get_modal_template()
        find.assert_called_with(
            ["base_templates/form_modal_base.html"]
        )

    def test_get_modal_template_does_not_exist(self):
        self.assertEqual(None, Subrecord.get_modal_template())

    @patch('opal.models.find_template')
    @patch('opal.models.Subrecord.get_form_template')
    def test_modal_template_no_form_template(self, modal, find):
        modal.return_value = None
        Subrecord.get_modal_template()
        find.assert_called_with([os.path.join('modals', 'subrecord_modal.html')])

    def test_get_normal_field_title(self):
        name_title = PatientColour._get_field_title("name")
        self.assertEqual(name_title, "Name")

    def test_get_foreign_key_or_free_text_title(self):
        dog_title = DogOwner._get_field_title("dog")
        self.assertEqual(dog_title, "Dog")

    def test_get_title_over_many_to_many(self):
        hats = HatWearer._get_field_title("hats")
        self.assertEqual(hats, "Hats")

    def test_get_title_over_reverse_foreign_key(self):
        houses = HouseOwner._get_field_title("house")
        self.assertEqual(houses, "Houses")

    def test_verbose_name(self):
        only_words = FamousLastWords._get_field_title("words")
        self.assertEqual(only_words, "Only Words")

    def test_enum(self):
        enum = FavouriteColour.get_field_enum('name')
        self.assertEqual(enum, ["purple", "yellow", "blue"])

    def test_description(self):
        description = FavouriteColour.get_field_description('name')
        self.assertEqual(description, "orange is the new black")

    def test_verbose_name_abbreviation(self):
        # if a word is an abbreviation already, don't title case it!
        osd = DogOwner._get_field_title("ownership_start_date")
        self.assertEqual(osd, "OSD")

    def test_get_defaults(self):
        self.assertEqual("Catherine", DogOwner._get_field_default("name"))

    def test_callable_defaults(self):
        self.assertEqual("Philipa", HoundOwner._get_field_default("name"))

    def test_defaults_if_there_are_no_defaults(self):
        self.assertEqual(None, HatWearer._get_field_default("name"))

    def test_get_defaults_from_free_text_and_foreign_key(self):
        self.assertEqual("spaniel", DogOwner._get_field_default("dog"))

    def test_get_defaults_from_free_text_and_foreign_key_lambda(self):
        self.assertEqual("spaniel", HoundOwner._get_field_default("dog"))

    def test_get_defaults_from_reverse_foreign_key(self):
        houses = HouseOwner._get_field_default("house")
        self.assertEqual([], houses)

    def test_get_defaults_from_ftfk_when_there_are_no_defaults(self):
        self.assertEqual(None, Colour._get_field_default("name"))

    def test_get_defaults_with_an_datetime_throws_an_error(self):
        name = Colour._meta.get_field("name")
        with patch.object(name, "get_default") as get_default:
            get_default.return_value = datetime.datetime.now()
            with self.assertRaises(exceptions.APIError):
                Colour._get_field_default("name")

    def test_get_defaults_with_a_date_throws_an_error(self):
        name = Colour._meta.get_field("name")
        with patch.object(name, "get_default") as get_default:
            get_default.return_value = datetime.date.today()
            with self.assertRaises(exceptions.APIError):
                Colour._get_field_default("name")


class BulkUpdateFromDictsTest(OpalTestCase):

    def test_bulk_update_from_dict(self):
        self.assertFalse(PatientColour.objects.exists())
        patient_colours = [
            {"name": "purple"},
            {"name": "blue"}
        ]
        patient = Patient.objects.create()
        colours = PatientColour.bulk_update_from_dicts(
            patient, patient_colours, self.user
        )
        expected_patient_colours = set(["purple", "blue"])
        new_patient_colours = set(PatientColour.objects.values_list(
            "name", flat=True
        ))
        self.assertEqual(
            expected_patient_colours, new_patient_colours
        )
        self.assertEqual(colours[0].name, "purple")
        self.assertEqual(colours[1].name, "blue")

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
        colours = PatientColour.bulk_update_from_dicts(
            patient, patient_colours, self.user
        )
        expected_patient_colours = ["purple", "blue"]
        new_patient_colours = list(PatientColour.objects.values_list(
            "name", flat=True
        ))
        self.assertEqual(
            expected_patient_colours, new_patient_colours
        )
        self.assertEqual(
            expected_patient_colours, [i.name for i in colours]
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

        with self.assertRaises(exceptions.MissingConsistencyTokenError):
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
        self.assertEqual(result.words, list(famous_last_words[0].values())[0])


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

    def test_update_from_dict_no_id_or_patient_id(self):
        a = InpatientAdmission()
        with self.assertRaises(ValueError):
            a.update_from_dict({})


class PatientConsultationTestCase(OpalTestCase):
    def setUp(self):
        _, self.episode = self.new_patient_and_episode_please()
        self.patient_consultation = PatientConsultation.objects.create(
            episode_id=self.episode.id
        )

    def test_if_when_is_set(self):
        when = datetime.datetime(2016, 6, 10, 12, 2, 20)
        patient_consultation_dict = dict(
            when='10/06/2016 12:02:20',
        )

        self.patient_consultation.update_from_dict(patient_consultation_dict, self.user)
        patient_consultation = self.episode.patientconsultation_set.first()
        self.assertEqual(patient_consultation.when.year, when.year)
        self.assertEqual(patient_consultation.when.month, when.month)
        self.assertEqual(patient_consultation.when.day, when.day)

    def test_if_when_is_not_set(self):
        now = timezone.now()
        patient_consultation_dict = dict()
        self.patient_consultation.update_from_dict(patient_consultation_dict, self.user)
        patient_consultation = self.episode.patientconsultation_set.first()
        self.assertTrue(patient_consultation.when >= now)


class SymptomComplexTestCase(OpalTestCase):
    def setUp(self):
        self.patient, self.episode = self.new_patient_and_episode_please()
        super(SymptomComplexTestCase, self).setUp()
        self.symptom_1 = Symptom.objects.create(name="tiredness")
        self.symptom_2 = Symptom.objects.create(name="alertness")
        self.symptom_3 = Symptom.objects.create(name="apathy")
        self.symptom_complex = SymptomComplex.objects.create(
            duration="a week",
            details="information",
            consistency_token=1111,
            episode=self.episode
        )
        self.symptom_complex.symptoms.add(self.symptom_2, self.symptom_3)

    def test_to_dict(self):
        expected_data = dict(
            id=self.symptom_complex.id,
            consistency_token=self.symptom_complex.consistency_token,
            symptoms=["alertness", "apathy"],
            duration="a week",
            details="information",
            episode_id=self.symptom_complex.episode.id,
            updated=None,
            updated_by_id=None,
            created=None,
            created_by_id=None
        )
        self.assertEqual(
            expected_data, self.symptom_complex.to_dict(self.user)
        )

    def test_update_from_dict(self):
        data = {
            u'consistency_token': self.symptom_complex.consistency_token,
            u'id': self.symptom_complex.id,
            u'symptoms': [u'alertness', u'tiredness'],
            u'duration': 'a month',
            u'details': 'other information'
        }
        self.symptom_complex.update_from_dict(data, self.user)
        new_symptoms = self.symptom_complex.symptoms.values_list(
            "name", flat=True
        )
        self.assertEqual(set(new_symptoms), set([u'alertness', u'tiredness']))
        self.assertEqual(self.symptom_complex.duration, 'a month')
        self.assertEqual(
            self.symptom_complex.details, 'other information'
        )


class TaggingTestCase(OpalTestCase):
    def test_display_template(self):
        self.assertEqual('tagging.html', Tagging.get_display_template())

    def test_form_template(self):
        self.assertEqual('tagging_modal.html', Tagging.get_form_template())

    @patch.object(patient_lists.TaggedPatientList, "list")
    def test_field_schema(self, patient_list):
        patient_list.return_value = [test_patient_lists.TaggingTestPatientList]
        expected = [
            {'name': 'eater', 'title': 'Eater', 'type': 'boolean'},
            {'type': 'boolean', 'name': 'herbivore', 'title': 'Herbivore'}
        ]
        schema = Tagging.build_field_schema()
        self.assertEqual(expected, schema)


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


class ContactNumberTestCase(OpalTestCase):

    def test_str(self):
        c = models.ContactNumber(name='Jane Doe', number='0777383828')
        self.assertEqual('Jane Doe: 0777383828', c.__str__())


class SynonymTestCase(OpalTestCase):

    def test_str(self):
        s = models.Synonym(name='Name')
        self.assertEqual('Name', s.__str__())


class RoleTestCase(OpalTestCase):

    def test_str(self):
        r = models.Role(name='Doctor')
        self.assertEqual('Doctor', r.__str__())


class UserProfileTestCase(OpalTestCase):
    def test_create(self):
        user = User.objects.create()
        self.assertTrue(bool(user.profile))
