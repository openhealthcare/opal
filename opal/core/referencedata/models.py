"""
Opal Reference Data instances
"""
from opal.core import lookuplists

class Condition(lookuplists.LookupList):
    """
    A condition that a person may have e.g. Diabetes, Liver Failure
    """
    pass


class Country(lookuplists.LookupList):
    """
    Countries of the world
    """
    pass


class Drug(lookuplists.LookupList):
    """
    Names of drugs that may be given e.g. Rifampacin, Paracetamol
    """
    pass


class DrugAdverseEvent(lookuplists.LookupList):
    class Meta:
        verbose_name = "Drug adverse event"


class Drugfreq(lookuplists.LookupList):
    class Meta:
        verbose_name = "Drug frequency"
        verbose_name_plural = "Drug frequencies "


class Drugroute(lookuplists.LookupList):
    class Meta:
        verbose_name = "Drug route"


class Duration(lookuplists.LookupList):
    pass


class Ethnicity(lookuplists.LookupList):
    class Meta:
        verbose_name_plural = "Ethnicities"


class Gender(lookuplists.LookupList):
    pass


class Hospital(lookuplists.LookupList):
    pass


class MaritalStatus(lookuplists.LookupList):
    class Meta:
        verbose_name_plural = "Marital statuses"


class PatientConsultationReasonForInteraction(lookuplists.LookupList):
    class Meta:
        verbose_name_plural = "Patient advice reasons for interaction"


class ReferralOrganisation(lookuplists.LookupList):
    pass


class ReferralType(lookuplists.LookupList):
    pass


class Speciality(lookuplists.LookupList):
    """
    Clinical Specialities e.g. Respiratory, Oncology, Cardiology etc
    """
    class Meta:
        verbose_name_plural = "Specialities"


class Symptom(lookuplists.LookupList):
    pass


class Title(lookuplists.LookupList):
    pass


class TravelReason(lookuplists.LookupList):
    class Meta:
        verbose_name = "Travel reason"


class Ward(lookuplists.LookupList):
    """
    A Ward at a hospital.
    """
    pass
