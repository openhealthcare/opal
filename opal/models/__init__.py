"""
OPAL Models!
"""
import collections
import json

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.dispatch import receiver
from django.template import TemplateDoesNotExist
from django.template.loader import select_template
import reversion

from opal.core import application, exceptions, lookuplists, plugins
from opal import managers
from opal.utils import camelcase_to_underscore
from opal.core.fields import ForeignKeyOrFreeText
from opal.core.subrecords import episode_subrecords, patient_subrecords
from opal.models.mixins import UpdatesFromDictMixin

app = application.get_app()


class Filter(models.Model):
    """
    Saved filters for users extracting data.
    """
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    criteria = models.TextField()

    def to_dict(self):
        return dict(id=self.pk, name=self.name, criteria=json.loads(self.criteria))

    def update_from_dict(self, data):
        self.criteria = json.dumps(data['criteria'])
        self.name = data['name']
        self.save()


class ContactNumber(models.Model):
    name = models.CharField(max_length=255)
    number = models.CharField(max_length=255)

    def __unicode__(self):
        return u'{0}: {1}'.format(self.name, self.number)


class Team(models.Model):
    """
    A team to which an episode may be tagged

    Represents either teams or stages in patient flow.
    """
    HELP_RESTRICTED = "Whether this team is restricted to only a subset of users"

    name           = models.CharField(max_length=250,
                                      help_text="This should only have letters and underscores")
    title          = models.CharField(max_length=250)
    parent         = models.ForeignKey('self', blank=True, null=True)
    active         = models.BooleanField(default=True)
    order          = models.IntegerField(blank=True, null=True)
    #TODO: Move this somewhere else
    useful_numbers = models.ManyToManyField(ContactNumber, blank=True)
    restricted     = models.BooleanField(default=False,
                                         help_text=HELP_RESTRICTED)
    direct_add     = models.BooleanField(default=True)
    show_all       = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title

    @classmethod
    def restricted_teams(klass, user):
        """
        Given a USER, return the restricted teams this user can access.
        """
        restricted_teams = []
        for plugin in plugins.plugins():
            if plugin.restricted_teams:
                restricted_teams += plugin().restricted_teams(user)
        return restricted_teams

    @classmethod
    def for_user(klass, user):
        """
        Return the set of teams this user has access to.
        """

        profile, _ = UserProfile.objects.get_or_create(user=user)
        if profile.restricted_only:
            teams = []
        else:
            teams = klass.objects.filter(active=True, restricted=False).order_by('order')
        restricted_teams = klass.restricted_teams(user)
        allteams = list(teams) + restricted_teams
        teams = []
        for t in allteams:
            if t not in teams:
                teams.append(t)
        return teams

    @property
    def has_subteams(self):
        return self.team_set.count() > 0


class Synonym(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = (('name', 'content_type'))

    def __unicode__(self):
        return self.name


class LocatedModel(models.Model):
    address_line1 = models.CharField("Address line 1", max_length = 45,
                                     blank=True, null=True)
    address_line2 = models.CharField("Address line 2", max_length = 45,
                                     blank=True, null=True)
    city = models.CharField(max_length = 50, blank = True)
    county = models.CharField("County", max_length = 40,
                              blank=True, null=True)
    post_code = models.CharField("Post Code", max_length = 10,
                                 blank=True, null=True)

    class Meta:
        abstract = True


class GP(LocatedModel):
    name = models.CharField(blank=True, null=True, max_length=255)
    tel1 = models.CharField(blank=True, null=True, max_length=50)
    tel2 = models.CharField(blank=True, null=True, max_length=50)


class CommunityNurse(LocatedModel):
    name = models.CharField(blank=True, null=True, max_length=255)
    tel1 = models.CharField(blank=True, null=True, max_length=50)
    tel2 = models.CharField(blank=True, null=True, max_length=50)


class Macro(models.Model):
    """
    A Macro is a user-expandable text sequence that allows us to
    enter "github-style" #foo text blocks from an admin defined
    list and then have them expand to cover frequent entries.
    """
    HELP_TITLE = "This is the text that will display in the dropdown. No spaces!"
    HELP_EXPANDED = "This is thte text that it will expand to."

    title    = models.CharField(max_length=200, help_text=HELP_TITLE)
    expanded = models.TextField(help_text=HELP_EXPANDED)

    def __unicode__(self):
        return self.title

    @classmethod
    def to_dict(klass):
        """
        Return a serialised version of our Macros ready to be JSON'd
        """
        return [dict(expanded=m.expanded, label=m.title)
                for m in klass.objects.all()]


class Patient(models.Model):
    def __unicode__(self):
        try:
            demographics = self.demographics_set.get()
            return '%s | %s' % (demographics.hospital_number, demographics.name)
        except models.ObjectDoesNotExist:
            return 'Patient {0}'.format(self.id)
        except:
            print self.id
            raise

    def create_episode(self, category=None):
        return self.episode_set.create()

    def get_active_episode(self):
        for episode in self.episode_set.order_by('id').reverse():
            if episode.active:
                return episode
        return None

    def to_dict(self, user):
        active_episode = self.get_active_episode()
        d = {
            'id': self.id,
            'episodes': {episode.id: episode.to_dict(user) for episode in self.episode_set.all()},
            'active_episode_id': active_episode.id if active_episode else None,
            }

        for model in patient_subrecords():
            subrecords = model.objects.filter(patient_id=self.id)
            d[model.get_api_name()] = [subrecord.to_dict(user) for subrecord in subrecords]
        return d

    def update_from_demographics_dict(self, demographics_data, user):
        demographics = self.demographics_set.get()
        demographics.update_from_dict(demographics_data, user)


class Episode(UpdatesFromDictMixin, models.Model):
    """
    An individual episode of care.

    A patient may have many episodes of care, but this maps to one occasion
    on which they found themselves on "The List".
    """
    category          = models.CharField(max_length=200, default=app.default_episode_category)
    patient           = models.ForeignKey(Patient)
    active            = models.BooleanField(default=False)
    date_of_admission = models.DateField(null=True, blank=True)
    # TODO rename to date_of_discharge?
    discharge_date    = models.DateField(null=True, blank=True)
    date_of_episode   = models.DateField(blank=True, null=True)
    consistency_token = models.CharField(max_length=8)

    objects = managers.EpisodeManager()

    def __unicode__(self):
        try:
            demographics = self.patient.demographics_set.get()

            return '%s | %s | %s' % (demographics.hospital_number,
                                     demographics.name,
                                     self.date_of_admission)
        except models.ObjectDoesNotExist:
            return self.date_of_admission
        except AttributeError:
            return 'Episode: {0}'.format(self.pk)
        except Exception as e:
            print e.__class__
            return self.date_of_admission

    @property
    def is_discharged(self):
        """
        Predicate property to determine if we're discharged.
        """
        if not self.active:
            return True
        if self.discharge_date:
            return True
        return False

    def set_tag_names(self, tag_names, user):
        """
        1. Blitz dangling tags not in our current dict.
        2. Add new tags.
        3. Make sure that we set the Active boolean appropriately
        4. There is no step 4.
        """
        original_tag_names = self.get_tag_names(user)

        for tag_name in original_tag_names:
            if tag_name not in tag_names:
                params = {'team__name': tag_name}
                if tag_name == 'mine':
                    params['user'] = user
                self.tagging_set.get(**params).delete()

        for tag_name in tag_names:
            if tag_name not in original_tag_names:
                team = Team.objects.get(name=tag_name)
                if team.parent:
                    if team.parent.name not in tag_names:
                        self.tagging_set.create(team=team.parent)
                params = {'team': team}
                if tag_name == 'mine':
                    params['user'] = user
                self.tagging_set.create(**params)

        if len(tag_names) < 1:
            self.active = False
        elif tag_names == ['mine']:
            self.active = True
        elif not self.active:
            self.active = True
        self.save()

    def tagging_dict(self, user):
        td = [{
                t.team.name: True for t in
                self.tagging_set.select_related('team').exclude(team__name='mine').exclude(
                                                                team__isnull=True)
            }]
        if self.tagging_set.filter(team__name='mine', user=user).count() > 0:
            td[0]['mine'] = True
        td[0]['id'] = self.id
        return td

    def get_tag_names(self, user, historic=False):
        current = [t.team.name for t in self.tagging_set.all() if t.user in (None, user)]
        if not historic:
            return current
        historic = Tagging.historic_tags_for_episodes([self])[self.id].keys()
        return list(set(current + historic))

    def _episode_history_to_dict(self, user):
        """
        Return a serialised version of this patient's episode history
        """
        order = 'date_of_episode', 'date_of_admission', 'discharge_date'
        episode_history = self.patient.episode_set.order_by(*order)
        return [e.to_dict(user, shallow=True) for e in episode_history]

    def to_dict(self, user, shallow=False):
        """
        Serialisation to JSON for Episodes
        """
        d = {
            'id'               : self.id,
            'category'         : self.category,
            'active'           : self.active,
            'date_of_admission': self.date_of_admission,
            'date_of_episode'  : self.date_of_episode,
            'discharge_date'   : self.discharge_date,
            'consistency_token': self.consistency_token
            }
        if shallow:
            return d

        for model in patient_subrecords():
            subrecords = model.objects.filter(patient_id=self.patient.id)
            d[model.get_api_name()] = [subrecord.to_dict(user)
                                       for subrecord in subrecords]
        for model in episode_subrecords():
            subrecords = model.objects.filter(episode_id=self.id)
            d[model.get_api_name()] = [subrecord.to_dict(user)
                                       for subrecord in subrecords]

        d['tagging'] = self.tagging_dict(user)


        d['episode_history'] = self._episode_history_to_dict(user)
        return d


class Subrecord(UpdatesFromDictMixin, models.Model):
    consistency_token = models.CharField(max_length=8)

    _is_singleton = False

    class Meta:
        abstract = True

    def __unicode__(self):
        return u'{0}: {1}'.format(self.get_api_name(), self.id)

    @classmethod
    def get_api_name(cls):
        return camelcase_to_underscore(cls._meta.object_name)

    @classmethod
    def get_display_name(cls):
        if hasattr(cls, '_title'):
            return cls._title
        else:
            return cls._meta.object_name

    @classmethod
    def build_field_schema(cls):
        field_schema = []
        for fieldname in cls._get_fieldnames_to_serialize():
            if fieldname in ['id', 'patient_id', 'episode_id']:
                continue
            elif fieldname.endswith('_fk_id'):
                continue
            elif fieldname.endswith('_ft'):
                continue

            getter = getattr(cls, 'get_field_type_for_' + fieldname, None)
            if getter is None:
                field = cls._get_field_type(fieldname)
                if field in [models.CharField, ForeignKeyOrFreeText]:
                    field_type = 'string'
                else:
                    field_type = camelcase_to_underscore(field.__name__[:-5])
            else:
                field_type = getter()
            lookup_list = None
            if cls._get_field_type(fieldname) == ForeignKeyOrFreeText:
                fld = getattr(cls, fieldname)
                lookup_list = camelcase_to_underscore(fld.foreign_model.__name__)
            title = fieldname.replace('_', ' ').title()
            field_schema.append({'name': fieldname,
                                 'title': title,
                                 'type': field_type,
                                 'lookup_list': lookup_list})
        return field_schema

    @classmethod
    def get_display_template(cls, team=None, subteam=None):
        """
        Return the active display template for our record
        """
        name = camelcase_to_underscore(cls.__name__)
        list_display_templates = ['records/{0}.html'.format(name)]
        if team:
            list_display_templates.insert(
                0, 'records/{0}/{1}.html'.format(team, name))
            if subteam:
                list_display_templates.insert(
                    0, 'records/{0}/{1}/{2}.html'.format(team,
                                                              subteam,
                                                              name))
        try:
            return select_template(list_display_templates).template.name
        except TemplateDoesNotExist:
            return None

    @classmethod
    def get_detail_template(cls, team=None, subteam=None):
        """
        Return the active detail template for our record
        """
        name = camelcase_to_underscore(cls.__name__)
        templates = [
            'records/{0}_detail.html'.format(name),
            'records/{0}.html'.format(name)
        ]
        try:
            return select_template(templates).template.name
        except TemplateDoesNotExist:
            return None

    @classmethod
    def get_form_template(cls, team=None, subteam=None):
        """
        Return the active form template for our record
        """
        name = camelcase_to_underscore(cls.__name__)
        templates = ['modals/{0}_modal.html'.format(name)]
        if team:
            templates.insert(0, 'modals/{0}/{1}_modal.html'.format(
                team, name))
        if subteam:
            templates.insert(0, 'modals/{0}/{1}/{2}_modal.html'.format(
                team, subteam, name))
        try:
            return select_template(templates).template.name
        except TemplateDoesNotExist:
            return None


    def _to_dict(self, user, fieldnames):
        """
        Allow a subset of FIELDNAMES
        """
        d = {}
        for name in fieldnames:
            getter = getattr(self, 'get_' + name, None)
            if getter is not None:
                value = getter(user)
            else:
                value = getattr(self, name)
            d[name] = value

        return d

    def to_dict(self, user):
        return self._to_dict(user, self._get_fieldnames_to_serialize())


class PatientSubrecord(Subrecord):
    patient = models.ForeignKey(Patient)

    class Meta:
        abstract = True


class EpisodeSubrecord(Subrecord):
    episode = models.ForeignKey(Episode, null=False)

    class Meta:
        abstract = True


class Tagging(models.Model):
    _is_singleton = True
    _title = 'Teams'

    team = models.ForeignKey(Team, blank=True, null=True)
    user = models.ForeignKey(User, null=True, blank=True)
    episode = models.ForeignKey(Episode, null=False)

    def __unicode__(self):
        if self.user is not None:
            return 'User: %s - %s' % (self.user.username, self.team.name)
        else:
            return self.team.name

    @staticmethod
    def get_api_name():
        return 'tagging'

    @staticmethod
    def get_display_name():
        return 'Teams'

    @staticmethod
    def get_display_template(team=None, subteam=None):
        return 'tagging.html'

    @staticmethod
    def get_form_template(team=None, subteam=None):
        return 'tagging_modal.html'

    @staticmethod
    def build_field_schema():
        teams = [{'name': t.name, 'type':'boolean'} for t in Team.objects.filter(active=True)]
        return teams

    @classmethod
    def historic_tags_for_episodes(cls, episodes):
        """
        Given a list of episodes, return a dict indexed by episode id
        that contains historic tags for those episodes.
        """
        teams = {t.id: t.name for t in Team.objects.all()}
        deleted = reversion.get_deleted(cls)
        historic = collections.defaultdict(dict)
        for d in deleted:
            data = json.loads(d.serialized_data)[0]['fields']
            if data['episode'] in episodes:
                if 'team' in data:
                    if data['team'] in teams:
                        tag_name = teams[data['team']]
                    else:
                        print 'Team has been deleted since it was serialised.'
                        print 'We ignore these for now.'
                        continue
                else:
                    try:
                        tag_name = data['tag_name']
                    except KeyError:
                        print json.dumps(data, indent=2)
                        raise exceptions.FTWLarryError("Can't find the team in this data :(")

                historic[data['episode']][tag_name] = True
        return historic

    @classmethod
    def historic_episodes_for_tag(cls, tag):
        """
        Given a TAG return a list of episodes that have historically been
        tagged with it.
        """
        teams = {t.id: t.name for t in Team.objects.all()}
        deleted = reversion.get_deleted(cls)
        eids = set()
        for d in deleted:
            data = json.loads(d.serialized_data)[0]['fields']
            try:
                team_index = data['team']
                if team_index not in teams:
                    print "Can't find deleted team by index - we think the team has been deleted? "
                    print "DATA:"
                    print json.dumps(data, indent=2)
                    print "TEAMS:"
                    print json.dumps(teams, indent=2)
                    continue
                tag_name = teams[team_index]

            except KeyError:
                tag_name = data['tag_name']

            if tag_name == tag:
                eids.add(data['episode'])

        historic = Episode.objects.filter(id__in=eids)
        return historic


"""
Base Lookup Lists
"""

class Antimicrobial_route(lookuplists.LookupList):
    class Meta:
        verbose_name = "Antimicrobial route"


class Antimicrobial(lookuplists.LookupList): pass


class Antimicrobial_adverse_event(lookuplists.LookupList):
    class Meta:
        verbose_name = "Antimicrobial adverse event"


class Antimicrobial_frequency(lookuplists.LookupList):
    class Meta:
        verbose_name = "Antimicrobial frequency"
        verbose_name_plural = "Antimicrobial frequencies"


class Clinical_advice_reason_for_interaction(lookuplists.LookupList):
    class Meta:
        verbose_name = "Clinical advice reason for interaction"
        verbose_name_plural = "Clinical advice reasons for interaction"

class Condition(lookuplists.LookupList): pass
class Destination(lookuplists.LookupList): pass
class Drug(lookuplists.LookupList): pass


class Drugfreq(lookuplists.LookupList):
    class Meta:
        verbose_name = "Drug frequency"
        verbose_name_plural = "Drug frequencies "


class Drugroute(lookuplists.LookupList):
    class Meta:
        verbose_name = "Drug route"


class Duration(lookuplists.LookupList): pass


class Ethnicity(lookuplists.LookupList):
    class Meta:
        verbose_name_plural = "Ethnicities"


class Gender(lookuplists.LookupList): pass
class Hospital(lookuplists.LookupList): pass
class Ward(lookuplists.LookupList): pass


# These should probably get refactored into opal-opat in 0.5
class Line_complication(lookuplists.LookupList):
    class Meta:
        verbose_name = "Line complication"


class Line_removal_reason(lookuplists.LookupList):
    class Meta:
        verbose_name = "Line removal reason"


class Line_site(lookuplists.LookupList):
    class Meta:
        verbose_name = "Line site"


class Line_type(lookuplists.LookupList):
    class Meta:
        verbose_name = "Line type"


class Micro_test_c_difficile(lookuplists.LookupList):
    class Meta:
        verbose_name = "Micro test C difficile"
        verbose_name_plural = "Micro tests C difficile"


class Micro_test_csf_pcr(lookuplists.LookupList):
    class Meta:
        verbose_name = "Micro test CSF PCR"
        verbose_name_plural = "Micro tests CSF PCR"


class Micro_test_ebv_serology(lookuplists.LookupList):
    class Meta:
        verbose_name = "Micro test EBV serology"
        verbose_name_plural = "Micro tests EBV serology"


class Micro_test_hepititis_b_serology(lookuplists.LookupList):
    class Meta:
        verbose_name = "Micro test hepatitis B serology"
        verbose_name_plural = "Micro tests hepatitis B serology"


class Micro_test_hiv(lookuplists.LookupList):
    class Meta:
        verbose_name = "Micro test HIV"
        verbose_name_plural = "Micro tests HIV"


class Micro_test_leishmaniasis_pcr(lookuplists.LookupList):
    class Meta:
        verbose_name = "Micro test leishmaniasis PCR"
        verbose_name_plural = "Micro tests leishmaniasis PCR"


class Micro_test_mcs(lookuplists.LookupList):
    class Meta:
        verbose_name = "Micro test MCS"
        verbose_name_plural = "Micro tests MCS"


class Micro_test_other(lookuplists.LookupList):
    class Meta:
        verbose_name = "Micro test other"
        verbose_name_plural = "Micro tests other"

class Micro_test_parasitaemia(lookuplists.LookupList):
    class Meta:
        verbose_name = "Micro test parasitaemia"
        verbose_name_plural = "Micro tests parasitaemia"


class Micro_test_respiratory_virus_pcr(lookuplists.LookupList):
    class Meta:
        verbose_name = "Micro test respiratory virus PCR"
        verbose_name_plural = "Micro tests respiratory virus PCR"


class Micro_test_serology(lookuplists.LookupList):
    class Meta:
        verbose_name = "Micro test serology"
        verbose_name_plural = "Micro tests serology"


class Micro_test_single_igg_test(lookuplists.LookupList):
    class Meta:
        verbose_name = "Micro test single IgG test"
        verbose_name_plural = "Micro tests single IgG test"


class Micro_test_single_test_pos_neg(lookuplists.LookupList):
    class Meta:
        verbose_name = "Micro test single test pos neg"
        verbose_name_plural = "Micro tests single test pos neg"


class Micro_test_single_test_pos_neg_equiv(lookuplists.LookupList):
    class Meta:
        verbose_name = "Micro test single test pos neg equiv"
        verbose_name_plural = "Micro tests single test pos neg equiv"


class Micro_test_stool_parasitology_pcr(lookuplists.LookupList):
    class Meta:
        verbose_name = "Micro test stool parasitology PCR"
        verbose_name_plural = "Micro tests stool parasitology PCR"


class Micro_test_stool_pcr(lookuplists.LookupList):
    class Meta:
        verbose_name = "Micro test stool PCR"
        verbose_name_plural = "Micro tests stool PCR"


class Micro_test_swab_pcr(lookuplists.LookupList):
    class Meta:
        verbose_name = "Micro test swab PCR"
        verbose_name_plural = "Micro tests swab PCR"


class Micro_test_syphilis_serology(lookuplists.LookupList):
    class Meta:
        verbose_name = "Micro test syphilis serology"
        verbose_name_plural = "Micro tests syphilis serology"


class Micro_test_viral_load(lookuplists.LookupList):
    class Meta:
        verbose_name = "Micro test viral load"
        verbose_name_plural = "Micro tests viral load"


class Microbiology_organism(lookuplists.LookupList):
    class Meta:
        verbose_name = "Microbiology organism"


class Symptom(lookuplists.LookupList): pass


class Travel_reason(lookuplists.LookupList):
    class Meta:
        verbose_name = "Travel reason"


"""
Base models
"""


class Demographics(PatientSubrecord):
    _is_singleton = True
    _icon = 'fa fa-user'

    name             = models.CharField(max_length=255, blank=True)
    hospital_number  = models.CharField(max_length=255, blank=True)
    nhs_number       = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth    = models.DateField(null=True, blank=True)
    country_of_birth = ForeignKeyOrFreeText(Destination)
    ethnicity        = models.CharField(max_length=255, blank=True, null=True)
    gender           = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True


class Location(EpisodeSubrecord):
    _is_singleton = True
    _icon = 'fa fa-map-marker'

    category  = models.CharField(max_length=255, blank=True)
    hospital  = models.CharField(max_length=255, blank=True)
    ward      = models.CharField(max_length=255, blank=True)
    bed       = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        demographics = self.episode.patient.demographics_set.get()
        return u'Location for {0}({1}) {2} {3} {4} {5}'.format(
            demographics.name,
            demographics.hospital_number,
            self.category,
            self.hospital,
            self.ward,
            self.bed
            )


class Treatment(EpisodeSubrecord):
    _sort = 'start_date'
    _icon = 'fa fa-flask'
    _modal = 'lg'

    drug          = ForeignKeyOrFreeText(Drug)
    dose          = models.CharField(max_length=255, blank=True)
    route         = ForeignKeyOrFreeText(Drugroute)
    start_date    = models.DateField(null=True, blank=True)
    end_date      = models.DateField(null=True, blank=True)
    frequency     = ForeignKeyOrFreeText(Drugfreq)

    class Meta:
        abstract = True


class Allergies(PatientSubrecord):
    _icon = 'fa fa-warning'

    drug        = ForeignKeyOrFreeText(Drug)
    provisional = models.BooleanField(default=False)
    details     = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True


class Diagnosis(EpisodeSubrecord):
    """
    This is a working-diagnosis list, will often contain things that are
    not technically diagnoses, but is for historical reasons, called diagnosis.
    """
    _title = 'Diagnosis / Issues'
    _sort = 'date_of_diagnosis'
    _icon = 'fa fa-stethoscope'

    condition         = ForeignKeyOrFreeText(Condition)
    provisional       = models.BooleanField(default=False)
    details           = models.CharField(max_length=255, blank=True)
    date_of_diagnosis = models.DateField(blank=True, null=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return u'Diagnosis for {0}: {1} - {2}'.format(
            self.episode.patient.demographics_set.get().name,
            self.condition,
            self.date_of_diagnosis
            )


class PastMedicalHistory(EpisodeSubrecord):
    _title = 'PMH'
    _sort = 'year'
    _icon = 'fa fa-history'

    condition = ForeignKeyOrFreeText(Condition)
    year      = models.CharField(max_length=4, blank=True)
    details   = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True


class Investigation(EpisodeSubrecord):
    _title = 'Investigations'
    _sort = 'date_ordered'
    _icon = 'fa fa-crosshairs'
    _modal = 'lg'

    test                  = models.CharField(max_length=255)
    date_ordered          = models.DateField(null=True, blank=True)
    details               = models.CharField(max_length=255, blank=True)
    microscopy            = models.CharField(max_length=255, blank=True)
    organism              = models.CharField(max_length=255, blank=True)
    sensitive_antibiotics = models.CharField(max_length=255, blank=True)
    resistant_antibiotics = models.CharField(max_length=255, blank=True)
    result                = models.CharField(max_length=255, blank=True)
    igm                   = models.CharField(max_length=20, blank=True)
    igg                   = models.CharField(max_length=20, blank=True)
    vca_igm               = models.CharField(max_length=20, blank=True)
    vca_igg               = models.CharField(max_length=20, blank=True)
    ebna_igg              = models.CharField(max_length=20, blank=True)
    hbsag                 = models.CharField(max_length=20, blank=True)
    anti_hbs              = models.CharField(max_length=20, blank=True)
    anti_hbcore_igm       = models.CharField(max_length=20, blank=True)
    anti_hbcore_igg       = models.CharField(max_length=20, blank=True)
    rpr                   = models.CharField(max_length=20, blank=True)
    tppa                  = models.CharField(max_length=20, blank=True)
    viral_load            = models.CharField(max_length=20, blank=True)
    parasitaemia          = models.CharField(max_length=20, blank=True)
    hsv                   = models.CharField(max_length=20, blank=True)
    vzv                   = models.CharField(max_length=20, blank=True)
    syphilis              = models.CharField(max_length=20, blank=True)
    c_difficile_antigen   = models.CharField(max_length=20, blank=True)
    c_difficile_toxin     = models.CharField(max_length=20, blank=True)
    species               = models.CharField(max_length=20, blank=True)
    hsv_1                 = models.CharField(max_length=20, blank=True)
    hsv_2                 = models.CharField(max_length=20, blank=True)
    enterovirus           = models.CharField(max_length=20, blank=True)
    cmv                   = models.CharField(max_length=20, blank=True)
    ebv                   = models.CharField(max_length=20, blank=True)
    influenza_a           = models.CharField(max_length=20, blank=True)
    influenza_b           = models.CharField(max_length=20, blank=True)
    parainfluenza         = models.CharField(max_length=20, blank=True)
    metapneumovirus       = models.CharField(max_length=20, blank=True)
    rsv                   = models.CharField(max_length=20, blank=True)
    adenovirus            = models.CharField(max_length=20, blank=True)
    norovirus             = models.CharField(max_length=20, blank=True)
    rotavirus             = models.CharField(max_length=20, blank=True)
    giardia               = models.CharField(max_length=20, blank=True)
    entamoeba_histolytica = models.CharField(max_length=20, blank=True)
    cryptosporidium       = models.CharField(max_length=20, blank=True)

    class Meta:
        abstract = True

class Role(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return unicode(self.name)


class UserProfile(models.Model):
    """
    Profile for our user
    """
    HELP_RESTRICTED="This user will only see teams that they have been specifically added to"
    HELP_READONLY="This user will only be able to read data - they have no write/edit permissions"
    HELP_EXTRACT="This user will be able to download data from advanced searches"
    HELP_PW="Force this user to change their password on the next login"

    user                  = models.OneToOneField(User, related_name='profile')
    force_password_change = models.BooleanField(default=True, help_text=HELP_PW)
    can_extract           = models.BooleanField(default=False, help_text=HELP_EXTRACT)
    readonly              = models.BooleanField(default=False, help_text=HELP_READONLY)
    restricted_only       = models.BooleanField(default=False, help_text=HELP_RESTRICTED)
    roles                 = models.ManyToManyField(Role)

    def to_dict(self):
        return dict(
            readonly=self.readonly,
            can_extract=self.can_extract,
            filters=[f.to_dict() for f in self.user.filter_set.all()],
            roles=self.get_roles()
            )

    def get_roles(self):
        """
        Return a roles dictionary for this user
        """
        roles = {}
        for plugin in plugins.plugins():
            roles.update(plugin().roles(self.user))
        roles['default'] = [r.name for r in self.roles.all()]
        return roles

    def get_teams(self):
        """
        Return an iterable of teams for this user.
        """
        from opal.models import Team
        return Team.for_user(self.user)


@receiver(models.signals.post_save, sender=Patient)
def create_patient_singletons(sender, **kwargs):
    if kwargs['created']:
        patient = kwargs['instance']
        for subclass in patient_subrecords():
            if subclass._is_singleton:
                obj = subclass.objects.create(patient=patient)


@receiver(models.signals.post_save, sender=Episode)
def create_episode_singletons(sender, **kwargs):
    if kwargs['created']:
        episode = kwargs['instance']
        for subclass in episode_subrecords():
            if subclass._is_singleton:
                subclass.objects.create(episode=episode)
