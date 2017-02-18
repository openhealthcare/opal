"""
Declaring custom patient detail views.
"""
from opal import utils
from opal.core import discoverable


class BasePatientDetailView(discoverable.SortableFeature,
                            discoverable.DiscoverableFeature,
                            discoverable.RestrictableFeature):
    module_name = 'detail'


class PatientDetailView(BasePatientDetailView, utils.AbstractBase):
    slug         = None
    display_name = None
    template     = None
    visible      = None
    order        = None
