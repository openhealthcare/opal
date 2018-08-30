"""
Unittests for the opal.core.match module
"""
from opal.core.test import OpalTestCase
from opal.core import exceptions
from opal.models import Patient

from opal.core import match

class MatcherTestCase(OpalTestCase):

    def create_patient(self):
        """
        Helper function to create a patient with some standard data
        """
        p, e = self.new_patient_and_episode_please()
        demographics = p.demographics_set.get()
        demographics.first_name = 'Tony'
        demographics.surname = 'Williams'
        demographics.hospital_number = '8/923893'
        demographics.save()
        return p


    # __init__()
    def test_initialize_with_data(self):
        m = match.Matcher({})
        self.assertEqual({}, m.data)


    # _get_patient_from_demographics_kwargs()
    def test_get_patient_from_demographic_kwargs(self):
        p = self.create_patient()

        m = match.Matcher({})
        matched = m._get_patient_from_demographics_kwargs(
            dict(first_name='Tony', surname='Williams')
        )
        self.assertEqual(p.id, matched.id)

    def test_get_patient_from_demographic_kwargs_no_match(self):
        with self.assertRaises(exceptions.PatientNotFoundError):
            m = match.Matcher({})
            matched = m._get_patient_from_demographics_kwargs(
                dict(first_name='Tony', surname='Williams')
            )

    # get_demographic_dict()
    def test_get_demographic_dict(self):

        class MyMatcher(match.Matcher):
            demographics_fields = ['first_name', 'surname']

        data = {'first_name': 'Tony', 'surname': 'Williams', 'age': 73}
        m = MyMatcher(data)
        demographics_dict = m.get_demographic_dict()

        self.assertEqual({'first_name': 'Tony', 'surname': 'Williams'}, demographics_dict)

    def test_get_demographic_dict_with_mapping(self):
        class MyMatcher(match.Matcher):
            demographics_fields = [
                'first_name',
                match.Mapping('second_name', 'surname')
            ]

        data = {'first_name': 'Tony', 'second_name': 'Williams', 'age': 73}
        m = MyMatcher(data)
        demographics_dict = m.get_demographic_dict()

        self.assertEqual({'first_name': 'Tony', 'surname': 'Williams'}, demographics_dict)

    # direct_match()
    def test_direct_match_simple_field(self):
        p = self.create_patient()

        class MyMatcher(match.Matcher):
            direct_match_field = 'hospital_number'

        m = MyMatcher({'hospital_number': '8/923893'})

        patient = m.direct_match()
        self.assertEqual(p.id, patient.id)

    def test_direct_match_simple_field_no_patient(self):

        class MyMatcher(match.Matcher):
            direct_match_field = 'hospital_number'

        m = MyMatcher({'hospital_number': '8/923893'})
        with self.assertRaises(exceptions.PatientNotFoundError):
            m.direct_match()

    def test_direct_match_simple_field_no_value_in_data(self):
        p = self.create_patient()

        class MyMatcher(match.Matcher):
            direct_match_field = 'hospital_number'

        m = MyMatcher({'nhs_number': '8/923893'})
        with self.assertRaises(exceptions.PatientNotFoundError):
            m.direct_match()

    def test_direct_match_mapping(self):
        p = self.create_patient()

        class MyMatcher(match.Matcher):
            direct_match_field = match.Mapping('MRN', 'hospital_number')

        m = MyMatcher({'MRN': '8/923893'})

        patient = m.direct_match()
        self.assertEqual(p.id, patient.id)

    def test_direct_match_mapping_no_patient(self):

        class MyMatcher(match.Matcher):
            direct_match_field = match.Mapping('MRN', 'hospital_number')

        m = MyMatcher({'MRN': '8/923893'})
        with self.assertRaises(exceptions.PatientNotFoundError):
            m.direct_match()

    def test_direct_match_mapping_no_value_in_data(self):
        p = self.create_patient()

        class MyMatcher(match.Matcher):
            direct_match_field = match.Mapping('MRN', 'hospital_number')

        m = MyMatcher({'NHS_Number': '8/923893'})
        with self.assertRaises(exceptions.PatientNotFoundError):
            m.direct_match()

    # attribute_match()
    def test_attribute_match(self):
        p = self.create_patient()

        class MyMatcher(match.Matcher):
            attribute_match_fields = ['first_name', 'surname']

        m = MyMatcher({'first_name': 'Tony', 'surname': 'Williams'})

        patient = m.attribute_match()
        self.assertEqual(p.id, patient.id)

    def test_attribute_match_partial_match(self):
        p = self.create_patient()

        class MyMatcher(match.Matcher):
            attribute_match_fields = ['first_name', 'surname', 'hospital_number']

        m = MyMatcher({'first_name': 'Tony', 'surname': 'Williams'})

        with self.assertRaises(exceptions.PatientNotFoundError):
            patient = m.attribute_match()

    def test_attribute_match_no_match(self):

        class MyMatcher(match.Matcher):
            attribute_match_fields = ['first_name', 'surname']

        m = MyMatcher({'first_name': 'Tony', 'surname': 'Williams'})

        with self.assertRaises(exceptions.PatientNotFoundError):
            patient = m.attribute_match()


    def test_attribute_match_with_mappings(self):
        p = self.create_patient()

        class MyMatcher(match.Matcher):
            attribute_match_fields = [
                'first_name',
                match.Mapping('last_name', 'surname')
            ]

        m = MyMatcher({'first_name': 'Tony', 'last_name': 'Williams'})

        patient = m.attribute_match()
        self.assertEqual(p.id, patient.id)


    def test_attribute_match_with_mappings_partial_match(self):
        p = self.create_patient()

        class MyMatcher(match.Matcher):
            attribute_match_fields = [
                'first_name',
                match.Mapping('last_name', 'surname'),
                'hospital_number'
            ]

        m = MyMatcher({'first_name': 'Tony', 'surname': 'Williams'})

        with self.assertRaises(exceptions.PatientNotFoundError):
            patient = m.attribute_match()

    # match()
    def test_match_direct_match(self):
        p = self.create_patient()

        class MyMatcher(match.Matcher):
            direct_match_field = 'hospital_number'
            attribute_match_fields = ['first_name', 'surname']

        m = MyMatcher({'hospital_number': '8/923893'})

        patient = m.match()

        self.assertEqual(p.id, patient.id)

    def test_match_attribute_match(self):
        p = self.create_patient()

        class MyMatcher(match.Matcher):
            direct_match_field = 'hospital_number'
            attribute_match_fields = ['first_name', 'surname']

        m = MyMatcher({'first_name': 'Tony', 'surname': 'Williams'})

        patient = m.match()

        self.assertEqual(p.id, patient.id)

    def test_match_not_found(self):

        class MyMatcher(match.Matcher):
            direct_match_field = 'hospital_number'
            attribute_match_fields = ['first_name', 'surname']

        m = MyMatcher(
            {
                'first_name'     : 'Tony',
                'surname'        : 'Williams',
                'hospital_number': '8/923893'
            }
        )
        with self.assertRaises(exceptions.PatientNotFoundError):
            patient = m.match()


    # create()
    def test_creates_patient(self):

        class MyMatcher(match.Matcher):
            direct_match_field = 'hospital_number'
            attribute_match_fields = ['first_name', 'surname']
            demographics_fields = ['hospital_number', 'first_name', 'surname']

        m = MyMatcher(
            {
                'first_name'     : 'Tony',
                'surname'        : 'Williams',
                'hospital_number': '8/923893'
            }
        )

        m.create()
        patient = Patient.objects.get(demographics__hospital_number='8/923893')
        self.assertEqual(patient.demographics_set.get().first_name, 'Tony')
        self.assertEqual(patient.demographics_set.get().surname, 'Williams')

    # match_or_create()
    def test_match_patient(self):
        p = self.create_patient()

        class MyMatcher(match.Matcher):
            direct_match_field = 'hospital_number'
            attribute_match_fields = ['first_name', 'surname']
            demographics_fields = ['hospital_number', 'first_name', 'surname']

        m = MyMatcher(
            {
                'first_name'     : 'Tony',
                'surname'        : 'Williams',
                'hospital_number': '8/923893'
            }
        )

        patient, created = m.match_or_create()
        self.assertEqual(p.id, patient.id)
        self.assertEqual(created, False)

    def test_creates_patient(self):

        class MyMatcher(match.Matcher):
            direct_match_field = 'hospital_number'
            attribute_match_fields = ['first_name', 'surname']
            demographics_fields = ['hospital_number', 'first_name', 'surname']

        m = MyMatcher(
            {
                'first_name'     : 'Tony',
                'surname'        : 'Williams',
                'hospital_number': '8/923893'
            }
        )

        patient, created = m.match_or_create()
        self.assertEqual(patient.demographics_set.get().first_name, 'Tony')
        self.assertEqual(patient.demographics_set.get().surname, 'Williams')
        self.assertEqual(True, created)

        patient = Patient.objects.get(demographics__hospital_number='8/923893')
        self.assertEqual(patient.demographics_set.get().first_name, 'Tony')
        self.assertEqual(patient.demographics_set.get().surname, 'Williams')
