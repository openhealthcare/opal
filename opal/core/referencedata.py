"""
This module defines the core reference data models that come with OPAL
"""
from opal.core import lookuplists

class Antimicrobial_route(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Antimicrobial route"


class Antimicrobial(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'


class Antimicrobial_adverse_event(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Antimicrobial adverse event"


class Antimicrobial_frequency(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Antimicrobial frequency"
        verbose_name_plural = "Antimicrobial frequencies"


class Clinical_advice_reason_for_interaction(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Clinical advice reason for interaction"
        verbose_name_plural = "Clinical advice reasons for interaction"

class Condition(lookuplists.LookupList): 
    class Meta:
        app_label = 'opal'

class Destination(lookuplists.LookupList): 
    class Meta:
        app_label = 'opal'

class Drug(lookuplists.LookupList): 
    class Meta:
        app_label = 'opal'


class Drugfreq(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Drug frequency"
        verbose_name_plural = "Drug frequencies "


class Drugroute(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Drug route"


class Duration(lookuplists.LookupList): 
    class Meta:
        app_label = 'opal'


class Ethnicity(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name_plural = "Ethnicities"


class Gender(lookuplists.LookupList): 
    class Meta:
        app_label = 'opal'

class Hospital(lookuplists.LookupList): 
    class Meta:
        app_label = 'opal'

class Ward(lookuplists.LookupList): 
    class Meta:
        app_label = 'opal'
        
class Speciality(lookuplists.LookupList): 
    class Meta:
        app_label = 'opal'

# These should probably get refactored into opal-opat in 0.5
class Line_complication(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Line complication"


class Line_removal_reason(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Line removal reason"


class Line_site(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Line site"


class Line_type(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Line type"


class Micro_test_c_difficile(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Micro test C difficile"
        verbose_name_plural = "Micro tests C difficile"


class Micro_test_csf_pcr(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Micro test CSF PCR"
        verbose_name_plural = "Micro tests CSF PCR"


class Micro_test_ebv_serology(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Micro test EBV serology"
        verbose_name_plural = "Micro tests EBV serology"


class Micro_test_hepititis_b_serology(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Micro test hepatitis B serology"
        verbose_name_plural = "Micro tests hepatitis B serology"


class Micro_test_hiv(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Micro test HIV"
        verbose_name_plural = "Micro tests HIV"


class Micro_test_leishmaniasis_pcr(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Micro test leishmaniasis PCR"
        verbose_name_plural = "Micro tests leishmaniasis PCR"


class Micro_test_mcs(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Micro test MCS"
        verbose_name_plural = "Micro tests MCS"


class Micro_test_other(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Micro test other"
        verbose_name_plural = "Micro tests other"

class Micro_test_parasitaemia(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Micro test parasitaemia"
        verbose_name_plural = "Micro tests parasitaemia"


class Micro_test_respiratory_virus_pcr(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Micro test respiratory virus PCR"
        verbose_name_plural = "Micro tests respiratory virus PCR"


class Micro_test_serology(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Micro test serology"
        verbose_name_plural = "Micro tests serology"


class Micro_test_single_igg_test(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Micro test single IgG test"
        verbose_name_plural = "Micro tests single IgG test"


class Micro_test_single_test_pos_neg(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Micro test single test pos neg"
        verbose_name_plural = "Micro tests single test pos neg"


class Micro_test_single_test_pos_neg_equiv(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Micro test single test pos neg equiv"
        verbose_name_plural = "Micro tests single test pos neg equiv"


class Micro_test_stool_parasitology_pcr(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Micro test stool parasitology PCR"
        verbose_name_plural = "Micro tests stool parasitology PCR"


class Micro_test_stool_pcr(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Micro test stool PCR"
        verbose_name_plural = "Micro tests stool PCR"


class Micro_test_swab_pcr(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Micro test swab PCR"
        verbose_name_plural = "Micro tests swab PCR"


class Micro_test_syphilis_serology(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Micro test syphilis serology"
        verbose_name_plural = "Micro tests syphilis serology"


class Micro_test_viral_load(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Micro test viral load"
        verbose_name_plural = "Micro tests viral load"


class Microbiology_organism(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Microbiology organism"


class Symptom(lookuplists.LookupList): 
    class Meta:
        app_label = 'opal'


class Travel_reason(lookuplists.LookupList):
    class Meta:
        app_label = 'opal'
        verbose_name = "Travel reason"

