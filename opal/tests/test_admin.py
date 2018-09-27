"""
Unittests for opal.admin
"""
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.sites import AdminSite

from opal.core.test import OpalTestCase
from opal.tests.models import Hat
from opal.models import Synonym, Patient, Episode

from opal.admin import (LookupListForm, PatientAdmin, EpisodeAdmin,
                        UserProfileAdmin)


class HatForm(LookupListForm):
    class Meta:
        model = Hat
        fields = '__all__'


class AdminTestCase(OpalTestCase):
    """
    A helper class that creates a patient, episode and the
    relevant Django sites framework object to pass into your
    admin instance.
    """
    def setUp(self):
        self.patient, self.episode = self.new_patient_and_episode_please()
        self.site = AdminSite()


class UserProfileAdminTestCase(AdminTestCase):

    def test_get_actions(self):
        request = self.rf.get('/admin/meh/')
        actions = UserProfileAdmin(self.user, self.site).get_actions(request)
        self.assertNotIn('delete_selected', actions)

    def test_delete_permission_obj_is_none(self):
        request = self.rf.get('/admin/meh/')
        request.user = self.user
        admin = UserProfileAdmin(self.user, self.site)
        has_perm = admin.has_delete_permission(request)
        self.assertTrue(has_perm)

    def test_delete_permission_has_created_subrecord(self):
        dem = self.patient.demographics()
        dem.created_by = self.user
        dem.save()
        request = self.rf.get('/admin/meh/')
        request.user = self.user
        admin = UserProfileAdmin(self.user, self.site)
        has_perm = admin.has_delete_permission(request, obj=self.user)
        self.assertFalse(has_perm)

    def test_delete_permission_has_updated_subrecord(self):
        dem = self.patient.demographics()
        dem.updated_by = self.user
        dem.save()
        request = self.rf.get('/admin/meh/')
        request.user = self.user
        admin = UserProfileAdmin(self.user, self.site)
        has_perm = admin.has_delete_permission(request, obj=self.user)
        self.assertFalse(has_perm)

    def test_delete_permission_has_created_episode(self):
        self.episode.created_by = self.user
        self.episode.save()
        request = self.rf.get('/admin/meh/')
        request.user = self.user
        admin = UserProfileAdmin(self.user, self.site)
        has_perm = admin.has_delete_permission(request, obj=self.user)
        self.assertFalse(has_perm)

    def test_delete_permission_has_updated_episode(self):
        self.episode.updated_by = self.user
        self.episode.save()
        request = self.rf.get('/admin/meh/')
        request.user = self.user
        admin = UserProfileAdmin(self.user, self.site)
        has_perm = admin.has_delete_permission(request, obj=self.user)
        self.assertFalse(has_perm)

    def test_delete_permission_has_created_tagging(self):
        self.episode.set_tag_names(['sssssh'], user=self.user)
        request = self.rf.get('/admin/meh/')
        request.user = self.user
        admin = UserProfileAdmin(self.user, self.site)
        has_perm = admin.has_delete_permission(request, obj=self.user)
        self.assertFalse(has_perm)

    def test_delete_permission_has_updated_tagging(self):
        self.episode.set_tag_names(['sssssh'], user=self.user)
        self.episode.set_tag_names([], user=self.user)
        request = self.rf.get('/admin/meh/')
        request.user = self.user
        admin = UserProfileAdmin(self.user, self.site)
        has_perm = admin.has_delete_permission(request, obj=self.user)
        self.assertFalse(has_perm)

    def test_delete_permission_has_been_lazy_and_done_nothing(self):
        request = self.rf.get('/admin/meh/')
        request.user = self.user
        admin = UserProfileAdmin(self.user, self.site)
        has_perm = admin.has_delete_permission(request, obj=self.user)
        self.assertTrue(has_perm)


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


class EpisodeAdminTestCase(AdminTestCase):
    def setUp(self):
        super(EpisodeAdminTestCase, self).setUp()
        self.admin = EpisodeAdmin(Episode, self.site)

    def test_episode_detail_link(self):
        self.assertEqual(
            self.admin.episode_detail_link(self.episode),
            "<a href='/#/patient/{0}/{1}'>/#/patient/{0}/{1}</a>".format(
                self.patient.id, self.episode.id
            )
        )

    def test_view_on_site(self):
        self.assertEqual(
            self.admin.view_on_site(self.episode),
            '/#/patient/{}/{}'.format(self.patient.id, self.episode.id)
        )


class PatientAdminTestCase(AdminTestCase):
    def setUp(self):
        super(PatientAdminTestCase, self).setUp()
        self.admin = PatientAdmin(Patient, self.site)

    def test_patient_detail_link(self):
        self.assertEqual(
            self.admin.patient_detail_link(self.patient),
            "<a href='/#/patient/{0}'>/#/patient/{0}</a>".format(
                self.patient.id
            )
        )

    def test_view_on_site(self):
        self.assertEqual(
            self.admin.view_on_site(self.patient),
            '/#/patient/{}'.format(self.patient.id)
        )
