"""
Declaring custom patient detail views.
"""
from opal.core import discoverable


class BasePatientDetailView(discoverable.SortableFeature,
                            discoverable.DiscoverableFeature,
                            discoverable.RestrictableFeature):
    module_name = 'detail'


class PatientDetailView(BasePatientDetailView):
    slug         = None
    display_name = None
    template     = None
    visible      = None
    order        = None
