from opal.admin import LookupListForm, PatientAdmin, EpisodeAdmin
from opal.core.test import OpalTestCase
from opal.tests.models import Hat
from opal.models import Synonym, Patient, Episode
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.sites import AdminSite


class HatForm(LookupListForm):
    class Meta:
        model = Hat
        fields = '__all__'


class LookupListFormTestCase(OpalTestCase):

    def test_invalid_synonym(self):
        hat = Hat.objects.create(name="Cowboy")
        ct = ContentType.objects.get_for_model(Hat)
        Synonym.objects.create(
            content_type=ct,
            object_id=hat.id,
            name="Stetson"
        )

        form = HatForm(dict(name="Stetson"))

        with self.assertRaises(ValueError):
            form.save()

    def test_valid_synonym(self):
        Hat.objects.create(name="Cowboy")
        form = HatForm()
        form.cleaned_data = dict(name="Stetson")
        self.assertEqual("Stetson", form.clean_name())


class AdminTestCase(OpalTestCase):
    def setUp(self):
        self.patient, self.episode = self.new_patient_and_episode_please()
        self.site = AdminSite()


class EpisodeAdminTestCase(AdminTestCase):
    def setUp(self):
        super(EpisodeAdminTestCase, self).setUp()
        self.admin = EpisodeAdmin(Episode, self.site)

    def test_episode_detail_link(self):
        self.assertEqual(
            self.admin.episode_detail_link(self.episode),
            "<a href='/#/patient/1/1'>/#/patient/1/1</a>"
        )

    def test_view_on_site(self):
        self.assertEqual(
            self.admin.view_on_site(self.episode),
            '/#/patient/1/1'
        )


class PatientAdminTestCase(AdminTestCase):
    def setUp(self):
        super(PatientAdminTestCase, self).setUp()
        self.admin = PatientAdmin(Patient, self.site)

    def test_patient_detail_link(self):
        self.assertEqual(
            self.admin.patient_detail_link(self.patient),
            "<a href='/#/patient/1'>/#/patient/1</a>"
        )

    def test_view_on_site(self):
        self.assertEqual(
            self.admin.view_on_site(self.patient),
            '/#/patient/1'
        )
