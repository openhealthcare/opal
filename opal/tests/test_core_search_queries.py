"""
unittests for opal.core.search.queries
"""
from django.contrib.auth.models import User

from opal.models import Episode, Patient
from opal.core.test import OpalTestCase

from opal.core.search import queries

class DatabaseQueryTestCase(OpalTestCase):

    def setUp(self):
        self.user    = User.objects.create(username='testuser')
        self.patient = Patient.objects.create()
        self.episode = self.patient.create_episode(category="testepisode")
        self.demographics = self.patient.demographics_set.get()
        self.demographics.name = 'Sally Stevens'
        self.demographics.gender = 'Female'
        self.demographics.save()
    
    def test_get_episodes(self):
        criteria = [
            {
                u'column'   : u'demographics', 
                u'field'    : u'Name', 
                u'combine'  : u'and', 
                u'query'    : u'Sally Stevens', 
                u'queryType': u'Equals'
            }
        ]
        query = queries.DatabaseQuery(self.user, criteria)
        self.assertEqual(set([self.episode]), query.get_episodes())

    def test_get_episodes_searching_ft_or_fk_field(self):
        criteria = [
            {
                u'column'   : u'demographics', 
                u'field'    : u'Gender',
                u'combine'  : u'and', 
                u'query'    : u'Female', 
                u'queryType': u'Equals'
            }
        ]
        query = queries.DatabaseQuery(self.user, criteria)
        self.assertEqual(set([self.episode]), query.get_episodes())
