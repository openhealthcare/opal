"""
Patient matching
"""
import collections
import datetime

from opal import models
from opal.core import exceptions, subrecords


Demographics = subrecords.get_subrecord_from_model_name('Demographics')
Mapping      = collections.namedtuple(
    'Mapping',
    ('data_fieldname', 'demographics_fieldname')
)


class Matcher(object):
    direct_match_field     = None
    attribute_match_fields = []
    demographics_fields    = []

    def __init__(self, data):
        """
        Access the data we're trying to match from self.data
        """
        self.data = data

    def _get_patient_from_demographics_kwargs(self, kwargs):
        try:
            return Demographics.objects.get(**kwargs).patient
        except (Demographics.DoesNotExist, models.Patient.DoesNotExist):
            raise exceptions.PatientNotFoundError()

    def get_demographic_dict(self):
        """
        Return the dictionary that could be passed to
        `Demographics.update_from_dict()`
        """
        demographics = {}
        for field in self.demographics_fields:
            if isinstance(field, Mapping):
                value = self.data[field.data_fieldname]
                demographics[field.demographics_fieldname] = value
            else:
                demographics[field] = self.data[field]
        return demographics

    def direct_match(self):
        """
        Return a patient matched directly against a unique identifier

        Raise PatientNotFoundError if a match is not found.
        """
        if isinstance(self.direct_match_field, Mapping):
            key    = self.direct_match_field.demographics_fieldname
            value  = self.data.get(self.direct_match_field.data_fieldname, None)
            if not value:
                raise exceptions.PatientNotFoundError(
                    'Blank direct match attribute in data'
                )
            kwargs = {key: value}
        else:
            kwargs = {
                self.direct_match_field: self.data.get(self.direct_match_field, None)
            }
        return self._get_patient_from_demographics_kwargs(kwargs)

    def attribute_match(self):
        """
        Return a patient matched exactly against three different attributes

        Raise PatientNotFoundError if a match is not found.
        """
        kwargs = {}
        for demographics_field in self.attribute_match_fields:
            if isinstance(demographics_field, Mapping):
                key         = demographics_field.demographics_fieldname
                value       = self.data.get(demographics_field.data_fieldname)
                kwargs[key] = value
            else:
                kwargs[demographics_field] = self.data.get(demographics_field)
        return self._get_patient_from_demographics_kwargs(kwargs)

    def match(self):
        """
        Return a Patient if they can be matched.

        Raise PatientNotFoundError if not.
        """
        try:
            return self.direct_match()
        except exceptions.PatientNotFoundError:
            return self.attribute_match()

    def create(self, user=None):
        """
        Create a patient from the demographics data provided.

        If required, pass in user as a kwarg.
        """
        patient = models.Patient.objects.create()
        patient.demographics_set.get().update_from_dict(
            self.get_demographic_dict(), user
        )
        return patient

    def match_or_create(self, user=None):
        """
        Either match an existing patient against the demographic
        data provided, or create one.

        If required, pass in user as a kwarg.

        Return a tuple of (Patient, bool) where bool is True if
        a patient has been created, and False if not.
        """
        try:
            return self.match(), False
        except exceptions.PatientNotFoundError:
            return self.create(user=user), True
