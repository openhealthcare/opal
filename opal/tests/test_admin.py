"""
Unittests for opal.admin
"""
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.urls import reverse

from opal.core.test import OpalTestCase
from opal.tests.models import Hat
from opal.models import Synonym, Patient, Episode, Role

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

    def test_create(self):
        role = Role.objects.create(name="can_doctor")
        post_dict = {
            # profile fields
             '_save': ['Save'],
            'profile-MIN_NUM_FORMS': ['0'],
            'profile-TOTAL_FORMS': ['1'],
            'profile-MAX_NUM_FORMS': ['1'],
            'profile-__prefix__-id': [''],
            'profile-0-id': [''],
            'profile-0-roles': [role.id],
            'profile-0-user': [''],
            'profile-INITIAL_FORMS': ['0'],
            'profile-__prefix__-force_password_change': ['on'],

            # user fields
            'username': ['test_user'],
            'email': [''],
            'password1': ['test1'],
            'password2': ['test1'],
            'first_name': [''],
            'last_name': [''],
        }
        url = reverse('admin:auth_user_add')
        self.assertTrue(
            self.client.login(
                username=self.user.username, password=self.PASSWORD
            )
        )
        response = self.client.post(url, post_dict)
        new_user = User.objects.get(username="test_user")
        self.assertEqual(
            list(new_user.profile.roles.values_list('name', flat=True)),
            ["can_doctor"]
        )

    def test_edit(self):
        self.assertTrue(
            self.client.login(
                username=self.user.username, password=self.PASSWORD
            )
        )
        new_user = User.objects.create(username="test_user")
        new_user.set_password("test1")
        new_user.save()
        profile = new_user.profile
        profile.force_password_change = False
        profile.save()
        role = Role.objects.create(name="can_doctor")
        url = reverse('admin:auth_user_change', args=(new_user.pk,))
        post_dict = {
            '_save': ['Save'],
            'first_name': [''],
            'username': ['test_user'],
            'last_name': [''],
            'email': [''],
            'last_login_0': [''],
            'last_login_1': [''],
            'date_joined_0': ['02/08/2019'],
            'date_joined_1': ['14:21:00'],
            'initial-date_joined_0': ['02/08/2019'],
            'initial-date_joined_1': ['14:21:00'],
            'is_active': ['on'],


            'profile-TOTAL_FORMS': ['1'],
            'profile-MAX_NUM_FORMS': ['1'],
            'profile-INITIAL_FORMS': ['1'],
            'profile-__prefix__-id': [''],
            'profile-__prefix__-user': [new_user.pk],
            'profile-0-force_password_change': ['on'],
            'profile-0-id': [new_user.profile.id],
            'profile-0-user': [new_user.id],
            'profile-0-roles': [role.id],
            'profile-__prefix__-force_password_change': ['on'],
            'profile-MIN_NUM_FORMS': ['0'],
        }
        response = self.client.post(url, post_dict)
        reloaded_user = User.objects.get(username="test_user")
        self.assertEqual(
            list(reloaded_user.profile.roles.values_list('name', flat=True)),
            ["can_doctor"]
        )


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
