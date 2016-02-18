"""
Unittests for opal.models
"""
from mock import patch
from opal.core.test import OpalTestCase
from opal.models import Subrecord, Tagging, Team, Patient
from django.contrib.auth.models import User


class SubrecordTestCase(OpalTestCase):

    @patch('opal.models.select_template')
    def test_display_template(self, select):
        Subrecord.get_display_template()
        select.assert_called_with(['records/subrecord.html'])

    @patch('opal.models.select_template')
    def test_display_template_team(self, select):
        Subrecord.get_display_template(team='test')
        select.assert_called_with([
            'records/test/subrecord.html',
            'records/subrecord.html',
        ])

    @patch('opal.models.select_template')
    def test_display_template_subteam(self, select):
        Subrecord.get_display_template(team='test', subteam='really')
        select.assert_called_with([
            'records/test/really/subrecord.html',
            'records/test/subrecord.html',
            'records/subrecord.html'
        ])

    @patch('opal.models.select_template')
    def test_detail_template(self, select):
        Subrecord.get_detail_template()
        select.assert_called_with([
            'records/subrecord_detail.html',
            'records/subrecord.html'
        ])

    @patch('opal.models.select_template')
    def test_detail_template_team(self, select):
        Subrecord.get_detail_template(team='test')
        select.assert_called_with([
            'records/subrecord_detail.html',
            'records/subrecord.html'
        ])

    @patch('opal.models.select_template')
    def test_detail_template_subteam(self, select):
        Subrecord.get_detail_template(team='test', subteam='really')
        select.assert_called_with(['records/subrecord_detail.html', 'records/subrecord.html'])

    @patch('opal.models.select_template')
    def test_form_template(self, select):
        Subrecord.get_form_template()
        select.assert_called_with(['modals/subrecord_modal.html'])

    @patch('opal.models.select_template')
    def test_modal_template_team(self, select):
        Subrecord.get_form_template(team='test')
        select.assert_called_with([
            'modals/test/subrecord_modal.html',
            'modals/subrecord_modal.html'
        ])

    @patch('opal.models.select_template')
    def test_modal_template_subteam(self, select):
        Subrecord.get_form_template(team='test', subteam='really')
        select.assert_called_with([
            'modals/test/really/subrecord_modal.html',
            'modals/test/subrecord_modal.html',
            'modals/subrecord_modal.html',
        ])

class TaggingImportTestCase(OpalTestCase):
    def test_tagging_import(self):
        import reversion
        from django.db import transaction
        patient = Patient.objects.create()

        with transaction.atomic(), reversion.create_revision():
            team_1 = Team.objects.create(name='team 0', title='team 1')
            team_2 = Team.objects.create(name='team 2', title='team 2')
            mine = Team.objects.create(name='mine', title='mine')
            user_1 = self.user
            user_2 = User.objects.create(
                username="someone",
                is_staff=False,
                is_superuser=False
            )

            # episode 1 has a tag and an archived tag
            episode_1 = patient.create_episode(
                category="testepisode",
            )

            # episode 2 had 1 tag, it was deleted, then it was readded
            episode_2 = patient.create_episode(
                category="testepisode",
            )

            # episode 3 has 2 tags and no new tags
            episode_3 = patient.create_episode(
                category="testepisode",
            )

            # episode 4 has no tags and 2 deleted tags
            episode_4 = patient.create_episode(
                category="testepisode",
            )

            # episode 5 has only user tags, 1 is deleted the other is not
            episode_5 = patient.create_episode(
                category="testepisode",
            )


            # episode 6 has only 1 user tag which has been deleted and replaced
            episode_6 = patient.create_episode(
                category="testepisode",
            )

            # episode 7 has a mixture of both types of user tags and episode tags
            episode_7 = patient.create_episode(
                category="testepisode",
            )

            # episode 1
            Tagging.objects.create(episode=episode_1, team=team_1)
            deleted_tag = Tagging.objects.create(episode=episode_1, team=team_2)

        with transaction.atomic(), reversion.create_revision():
            deleted_tag.delete()

        with transaction.atomic(), reversion.create_revision():
            deleted_tag = Tagging.objects.create(episode=episode_2, team=team_1)

        with transaction.atomic(), reversion.create_revision():
            deleted_tag.delete()

            # episode 2
            Tagging.objects.create(episode=episode_2, team=team_1)

            # episode 3
            Tagging.objects.create(episode=episode_3, team=team_1)
            Tagging.objects.create(episode=episode_3, team=team_2)

            # episode 4
            to_delete_1 = Tagging.objects.create(episode=episode_4, team=team_1)
            to_delete_2 = Tagging.objects.create(episode=episode_4, team=team_2)


        with transaction.atomic(), reversion.create_revision():
            to_delete_1.delete()
            to_delete_2.delete()

        # episode 5
        with transaction.atomic(), reversion.create_revision():
            Tagging.objects.create(episode=episode_5, team=mine, user=user_1)
            to_delete = Tagging.objects.create(episode=episode_5, team=mine, user=user_2)

        with transaction.atomic(), reversion.create_revision():
            to_delete.delete()

        # episode 6
        with transaction.atomic(), reversion.create_revision():
            to_delete = Tagging.objects.create(episode=episode_6, team=mine, user=user_1)

        with transaction.atomic(), reversion.create_revision():
            to_delete.delete()

        with transaction.atomic(), reversion.create_revision():
            Tagging.objects.create(episode=episode_6, team=mine, user=user_1)

        # episode 7
        with transaction.atomic(), reversion.create_revision():
            Tagging.objects.create(episode=episode_7, team=mine, user=user_1)
            to_delete_1 = Tagging.objects.create(episode=episode_7, team=mine, user=user_2)

            Tagging.objects.create(episode=episode_7, team=team_1)
            to_delete_2 = Tagging.objects.create(episode=episode_7, team=team_2)

        with transaction.atomic(), reversion.create_revision():
            to_delete_1.delete()
            to_delete_2.delete()

        Tagging.import_from_reversion()

        self.assertTrue(Tagging.objects.filter(
            episode=episode_1, team=team_1, archived=False
            ).exists()
        )
        self.assertTrue(Tagging.objects.filter(
            episode=episode_1, team=team_2, archived=True
            ).exists()
        )
        self.assertEqual(Tagging.objects.filter(episode=episode_1).count(), 2)

        self.assertTrue(Tagging.objects.filter(
            episode=episode_2, team=team_1, archived=False
            ).exists()
        )
        self.assertEqual(Tagging.objects.filter(episode=episode_2).count(), 1)

        self.assertTrue(Tagging.objects.filter(
            episode=episode_3, team=team_1, archived=False
            ).exists()
        )
        self.assertTrue(Tagging.objects.filter(
            episode=episode_3, team=team_2, archived=False
            ).exists()
        )
        self.assertEqual(Tagging.objects.filter(episode=episode_1).count(), 2)

        self.assertTrue(Tagging.objects.filter(
            episode=episode_4, team=team_1, archived=True
            ).exists()
        )
        self.assertTrue(Tagging.objects.filter(
            episode=episode_4, team=team_2, archived=True
            ).exists()
        )
        self.assertEqual(Tagging.objects.filter(episode=episode_1).count(), 2)

        self.assertTrue(Tagging.objects.filter(
            episode=episode_5, team=mine, user=user_1, archived=False
            ).exists()
        )
        self.assertTrue(Tagging.objects.filter(
            episode=episode_5, team=mine, user=user_2, archived=True
            ).exists()
        )
        self.assertEqual(Tagging.objects.filter(episode=episode_5).count(), 2)

        self.assertTrue(Tagging.objects.filter(
            episode=episode_6, team=mine, user=user_1, archived=False
            ).exists()
        )
        self.assertEqual(Tagging.objects.filter(episode=episode_6).count(), 1)

        self.assertTrue(Tagging.objects.filter(
            episode=episode_7, team=mine, user=user_1, archived=False
            ).exists()
        )
        self.assertTrue(Tagging.objects.filter(
            episode=episode_7, team=mine, user=user_2, archived=True
            ).exists()
        )
        self.assertTrue(Tagging.objects.filter(
            episode=episode_7, team=team_1, archived=False
            ).exists()
        )
        self.assertTrue(Tagging.objects.filter(
            episode=episode_7, team=team_2, archived=True
            ).exists()
        )
        self.assertEqual(Tagging.objects.filter(episode=episode_7).count(), 4)
