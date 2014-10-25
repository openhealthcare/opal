"""
Core re-usable OPAL models.
"""

"""
Lookup Lists
"""
from opal.utils.models import lookup_list

GenderLookupList = type(*lookup_list('gender', module='opal.models'))
EthnicityLookupList = type(*lookup_list('ethnicity', module='opal.models'))
