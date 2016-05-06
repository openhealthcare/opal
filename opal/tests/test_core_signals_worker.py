"""
Unittests to check that the signals defined in
opal.core.signals.worker are called at the appropriate
times and with the appropriate signature.
"""
from opal.core.test import OpalTestCase
from opal.models import Patient

class PatientPostSaveTestCase(OpalTestCase):
    def test_called(self):
        Patient
        pass
    # Register Signal mock
    # Create patient
    # Check signal mock called
