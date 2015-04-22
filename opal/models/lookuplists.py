"""
Lookup Lists
"""
from opal.core.lookuplists import lookup_list

GenderLookupList = type(*lookup_list('gender', module='opal.models'))
EthnicityLookupList = type(*lookup_list('ethnicity', module='opal.models'))
DestinationLookupList= type(*lookup_list('destination', module='opal.models'))
DrugLookupList= type(*lookup_list('drug', module='opal.models'))
DrugRouteLookupList= type(*lookup_list('drugroute', module='opal.models'))
DrugFrequencyLookupList= type(*lookup_list('drugfreq', module='opal.models'))
ConditionLookupList = type(*lookup_list('condition', module='opal.models'))
HospitalLookupList = type(*lookup_list('hospital', module='opal.models'))
