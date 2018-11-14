"""
Opal Pathways
"""
import inspect
import json
from collections import defaultdict

from django.urls import reverse
from django.db import models, transaction
from django.utils.text import slugify
from six import string_types

from opal.core import discoverable, menus, subrecords
from opal.utils import AbstractBase
from opal.core.serialization import OpalSerializer
from opal.core.pathway import Step


class RedirectsToPatientMixin(object):
    def redirect_url(self, user=None, patient=None, episode=None):
        return "/#/patient/{0}".format(patient.id)


class Pathway(discoverable.DiscoverableFeature):
    module_name        = "pathways"
    pathway_service    = "Pathway"
    finish_button_text = "Save"
    finish_button_icon = "fa fa-save"
    icon               = None
    display_name       = None

    # any iterable will do, this should be overridden
    steps = []

    @classmethod
    def get_slug(klass):
        """
        Returns a string which should be used as the slug for this pathway
        """
        slugattr = getattr(klass, 'slug', None)
        if slugattr:
            if isinstance(slugattr, string_types):
                return slugattr
        return slugify(klass.__name__)

    @classmethod
    def get_absolute_url(klass, **kwargs):
        """
        Returns a string which is the absolute URL of this Pathway.
        """
        return '{0}#/{1}/'.format(reverse('pathway_index'), klass.get_slug())

    @classmethod
    def get_icon(klass):
        """
        Default getter function - returns the `icon` property
        """
        return klass.icon

    @classmethod
    def get_display_name(klass):
        """
        Default getter function - returns the `display_name` property
        """
        return klass.display_name

    @classmethod
    def as_menuitem(kls, **kwargs):
        return menus.MenuItem(
            href=kwargs.get('href', kls.get_absolute_url()),
            activepattern=kwargs.get('activepattern', kls.get_absolute_url()),
            icon=kwargs.get('icon', kls.get_icon()),
            display=kwargs.get('display', kls.get_display_name()),
            index=kwargs.get('index', '')
        )

    def get_pathway_service(self, is_modal):
        return self.pathway_service

    @property
    def slug(self):
        return slugify(self.__class__.__name__)

    def get_template(self, is_modal):
        if is_modal:
            return self.modal_template
        return self.template

    def save_url(self, patient=None, episode=None):
        kwargs = dict(name=self.slug)

        if episode:
            kwargs["episode_id"] = episode.id

        if patient:
            kwargs["patient_id"] = patient.id

        return reverse("pathway", kwargs=kwargs)

    def redirect_url(self, user=None, patient=None, episode=None):
        episode = patient.episode_set.last()
        return "/#/patient/{0}/{1}".format(patient.id, episode.id)

    @transaction.atomic
    def save(self, data, user=None, patient=None, episode=None):
        if patient and not episode:
            episode = patient.create_episode()

        for step in self.get_steps():
            step.pre_save(
                data, user, patient=patient, episode=episode
            )

        # if there is an episode, remove unchanged subrecords
        if patient:
            data = self.remove_unchanged_subrecords(episode, data, user)
        else:
            # We can't import these at module load because we're imported by
            # opal.core.pathways.__init__
            from opal.models import Patient

            patient = Patient()

        patient.bulk_update(data, user, episode=episode)

        if not episode and patient.episode_set.count() == 1:
            episode = patient.episode_set.first()

        return patient, episode

    def remove_unchanged_subrecords(self, episode, new_data, user):

        # to_dict outputs dates as date() instances, but our incoming data
        # will be settings.DATE_FORMAT date strings. So we dump() then load()
        old_data = json.dumps(
            episode.to_dict(user),
            cls=OpalSerializer
        )
        old_data = json.loads(old_data)

        changed = defaultdict(list)

        for subrecord_class in subrecords.subrecords():
            subrecord_name = subrecord_class.get_api_name()
            old_subrecords = old_data.get(subrecord_name)
            new_subrecords = new_data.get(subrecord_name)

            if not new_subrecords:
                continue

            if not old_subrecords and new_subrecords:
                changed[subrecord_name] = new_subrecords
                continue

            id_to_old_subrecord = {i["id"]: i for i in old_subrecords}

            for new_subrecord in new_subrecords:
                if not new_subrecord.get("id"):
                    changed[subrecord_name].append(new_subrecord)
                else:
                    # schema doesn't translate these ids, so pop them out
                    old_subrecord = id_to_old_subrecord[new_subrecord["id"]]
                    old_subrecord.pop("episode_id", None)
                    old_subrecord.pop("patient_id", None)
                    if not new_subrecord == old_subrecord:
                        changed[subrecord_name].append(new_subrecord)
        return changed

    def get_steps(self, patient=None, episode=None, user=None):
        all_steps = []
        for step in self.steps:
            if inspect.isclass(step) and issubclass(step, models.Model):
                if step._is_singleton:
                    all_steps.append(Step(model=step))
                else:
                    all_steps.append(Step(model=step, multiple=True))
            else:
                all_steps.append(step)

        return all_steps

    def to_dict(self, is_modal, user=None, episode=None, patient=None):
        # the dict we json to send over
        # in theory it takes a list of either models or steps
        # in reality you can swap out steps for anything with a todict method
        # we need to have a template_url, title and an icon, optionally
        # it can take a step_controller with the name of the angular
        # controller
        steps = self.get_steps(user=user, episode=episode, patient=patient)

        steps_info = [i.to_dict() for i in steps]

        return dict(
            steps=steps_info,
            finish_button_text=self.finish_button_text,
            finish_button_icon=self.finish_button_icon,
            display_name=self.get_display_name(),
            icon=self.get_icon(),
            save_url=self.save_url(patient=patient, episode=episode),
            pathway_service=self.get_pathway_service(is_modal),
        )


class WizardPathway(Pathway, AbstractBase):
    pathway_service = "WizardPathway"
    template = "pathway/templates/wizard_pathway.html"
    modal_template = "pathway/templates/modal_wizard_pathway.html"


class PagePathway(Pathway, AbstractBase):
    """
    An unrolled pathway will display all of it's forms
    at once, rather than as a set of steps.
    """
    template = "pathway/templates/page_pathway.html"
    modal_template = "pathway/templates/modal_page_pathway.html"
