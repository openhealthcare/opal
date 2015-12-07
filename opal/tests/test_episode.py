"""
Unittests for Episodes
"""
import datetime

from django.contrib.auth.models import User

from opal.core.test import OpalTestCase
from opal.tests.models import Hat, HatWearer, Dog, DogOwner
from opal.models import Patient, Episode, Team


class EpisodeTest(OpalTestCase):

    def setUp(self):
        self.patient = Patient.objects.create()
        self.episode = self.patient.create_episode()
        self.hiv     = Team.objects.create(name='hiv', title='HIV')
        self.mine    = Team.objects.create(name='mine', title='Mine')
        self.micro   = Team.objects.create(name='microbiology', title='Microbiology')

    def test_singleton_subrecord_created(self):
        self.assertEqual(1, self.episode.episodename_set.count())

    def test_is_discharged_inactive(self):
        self.episode.active = False
        self.assertEqual(True, self.episode.is_discharged)

    def test_is_discharged_from_date(self):
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        self.episode.discharge_date = yesterday
        self.assertEqual(True, self.episode.is_discharged)

    def test_can_set_tag_names(self):
        for tag_names in [
            ['microbiology', 'mine'],
            ['microbiology', 'hiv'],
            ['hiv', 'mine'],
            ]:
            self.episode.set_tag_names(tag_names, self.user)
            self.assertEqual(set(tag_names),
                             set(self.episode.get_tag_names(self.user)))

    def test_user_cannot_see_other_users_mine_tag(self):
        other_user = User.objects.create(username='seconduser')

        self.episode.set_tag_names(['hiv', 'mine'], self.user)
        self.assertEqual(['hiv'], self.episode.get_tag_names(other_user))

    def test_active_if_tagged_by_non_mine_tag(self):
        self.episode.set_tag_names(['microbiology'], self.user)
        self.assertTrue(self.episode.active)

    def test_active_if_only_tagged_by_mine_tag(self):
        self.episode.set_tag_names(['mine'], self.user)
        self.assertTrue(self.episode.active)

    def test_to_dict_fields(self):
        as_dict = self.episode.to_dict(self.user)
        expected = [
            'id', 'category', 'active', 'date_of_admission', 'discharge_date',
            'consistency_token', 'date_of_episode'
        ]
        for field in expected:
            self.assertIn(field, as_dict)

    def test_to_dict_with_multiple_episodes(self):
        self.episode.date_of_admission = datetime.date(2015, 7, 25)
        self.episode.save()
        prev = self.patient.create_episode()
        prev.date_of_admission = datetime.date(2012, 7, 25)
        prev.discharge_date = datetime.date(2012, 8, 12)
        prev.active=False
        prev.save()

        serialised = self.episode.to_dict(self.user)
        self.assertEqual(2, len(serialised['episode_history']))
        self.assertEqual(datetime.date(2012, 7, 25),
                         serialised['episode_history'][0]['date_of_admission'])

    def test_to_dict_episode_ordering(self):
        patient = Patient.objects.create()
        prev = patient.create_episode()
        prev.date_of_admission = datetime.date(2012, 7, 25)
        prev.discharge_date = datetime.date(2012, 8, 12)
        prev.active = False
        prev.save()

        previouser = patient.create_episode()
        previouser.date_of_admission = datetime.date(2011, 7, 25)
        previouser.active = False
        previouser.save()

        episode = patient.create_episode()
        episode.date_of_admission = datetime.date(2014, 6, 23)
        episode.save()

        serialised = episode.to_dict(self.user)
        self.assertEqual(3, len(serialised['episode_history']))
        self.assertEqual(datetime.date(2011, 7, 25),
                         serialised['episode_history'][0]['date_of_admission'])
        self.assertEqual(datetime.date(2012, 7, 25),
                         serialised['episode_history'][1]['date_of_admission'])

    def test_to_dict_episode_history_includes_no_dates(self):
        prev = self.patient.create_episode()
        serialised = self.episode.to_dict(self.user)
        self.assertEqual(2, len(serialised['episode_history']))

    def test_to_dict_episode_with_many_to_many(self):
        prev = self.patient.create_episode()
        bowler = Hat.objects.create(name="bowler")
        top = Hat.objects.create(name="top")
        hw = HatWearer.objects.create(episode=prev)
        hw.hats.add(bowler, top)
        serialised = prev.to_dict(self.user)
        self.assertEqual(serialised["hat_wearer"][0]["hats"], [u'bowler', u'top'])


class EpisodeManagerTestCase(OpalTestCase):
    def setUp(self):
        self.patient = Patient.objects.create()
        self.episode = self.patient.create_episode()

        # make sure many to many serialisation goes as epected
        top = Hat.objects.create(name="top")
        hw = HatWearer.objects.create(episode=self.episode)
        hw.hats.add(top)

        # make sure free text or foreign key serialisation goes as expected
        # for actual foriegn keys
        Dog.objects.create(name="Jemima")
        do = DogOwner.objects.create(episode=self.episode)
        do.dog = "Jemima"
        do.save()

        # make sure it goes as expected for strings
        DogOwner.objects.create(episode=self.episode, dog="Philip")

    def test_serialised_fields(self):
        as_dict = Episode.objects.serialised(self.user, [self.episode])[0]
        expected = [
            'id', 'category', 'active', 'date_of_admission', 'discharge_date',
            'consistency_token', 'date_of_episode'
        ]

        for field in expected:
            self.assertIn(field, as_dict)

        dogs = set(i["dog"] for i in as_dict["dog_owner"])

        self.assertEqual(dogs, {"Jemima", "Philip"})
        self.assertEqual(as_dict["hat_wearer"][0]["hats"], ["top"])
