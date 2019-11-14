"""
Opal Forms Library
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.template.loader import get_template
from django.views.generic import TemplateView

from opal.core import subrecords
from opal.models import Patient, Episode, PatientSubrecord, EpisodeSubrecord
from opal.utils import _itersubclasses


#
# Form classes
#

class Form(object):

    @classmethod
    def get_name(klass):
        if hasattr(klass, 'name'):
            return klass.name
        return klass.__name__.lower()

    @classmethod
    def get_template_name(klass):
        return klass.template_name

    @classmethod
    def get(klass, name):
        for sub in _itersubclasses(klass):
            if sub.get_name() == name:
                return sub

    @classmethod
    def as_view(klass):

        class GeneratedView(FormView):
            form          = klass
            template_name = klass.get_template_name()

        return GeneratedView.as_view()

    def save(self, *args, **kwargs):
        raise NotImplementedError('Must implement the .save() of a Form')

    def get_redirect_url(self, *args, **kwargs):
        return redirect(kwargs['patient'].get_absolute_url())


class SubrecordForm(Form):
    model = None

    def __init__(self, *a, **k):
        self.instance = None
        if 'instance' in k:
            self.instance = k.pop('instance')
        super().__init__(*a, **k)

    def __str__(self):
        template = get_template(self.model.get_form_template())
        return template.render({'instance': self.instance})

    def consistency_token(self):
        if self.instance is None:
            return ''
        template = get_template('opal/forms/_consistency_token_field.html')
        return template.render({'instance': self.instance})

    def pre_save(self, **kwargs):
        """
        * Convert empty strings in date fields to None
        * Convert checkbox ON to True
        * Remove checkbox missing if it was previously true
        """
        data = {}
        for k, v in kwargs['data'].items():
            schema = self.model.build_schema_for_field_name(k)

            if schema['type'] == 'date':
                if v == "":
                    v = None
            if schema['type'] == 'boolean':
                if v == 'on':
                    v = True

            data[k] = v


        # The browser will simply omit boolean checkboxes if they've been
        # Un-ticked in this edit.
        if self.instance is not None:
            boolean_fields = [f for f in self.model.build_field_schema() if f['type'] == 'boolean']
            for field in boolean_fields:
                if field['name'] not in data:
                    if getattr(self.instance, field['name'], False):
                        data[field['name']] = False


        return data

    def save(self, data=None, user=None, patient=None, episode=None):
        ispatientsubrecord = issubclass(self.model, PatientSubrecord)
        isepisodesubrecord = issubclass(self.model, EpisodeSubrecord)

        if self.instance: # Edit
            if isepisodesubrecord:
                episode = self.instance.episode
                patient = episode.patient
            if ispatientsubrecord:
                patient = instance.patient
                episode = None

        else: # Create
            if not patient and not episode:
                patient = Patient.objects.create()

            if not episode:
                episode = patient.create_episode()
            else:
                patient = episode.patient

        if ispatientsubrecord:
            data['patient_id'] = patient.id

        elif isepisodesubrecord:
            data['episode_id'] = episode.id

        if self.model._is_singleton and not self.instance:
            if issubclass(self.model, PatientSubrecord):
                self.instance = self.model.objects.get(patient=patient)
            elif issubclass(self.model, EpisodeSubrecord):
                self.instance = self.model.objects.get(episode=episode)
        else:
            if not self.instance:
                self.instance = self.model()

        self.instance.update_from_dict(data, user)
        return patient, episode

#
# Form views
#
class FormView(LoginRequiredMixin, TemplateView):
    form = None

    def get_context_data(self, *a, **k):
        ctx = super().get_context_data(*a, **k)
        ctx['form'] = self.form_instance
        return ctx

    def get_form(self, *a, **k):
        return self.form

    def dispatch(self, *a, **k):
        if not hasattr(self, 'form_instance'):
            self.form_instance = self.get_form(*a, **k)()
        return super().dispatch(*a, **k)

    def post(self, *a, **k):
        """
        The POST method of a FormView:
        * strips Django artifacts from the data
        * checks for episode_id / patient_id in request kwargs and fetches them if so
        * passes data, user, and any episode/patient to the .save() method of the form
        * redirects to the .get_redirect_url() location
        """
        # Strip Django artifacts from POST to prepare data
        data = {k: v for k, v in self.request.POST.items() if k != 'csrfmiddlewaretoken'}
        print(self.request.POST)
        save_kwargs = {
            'data':data,
            'user': self.request.user
        }

        # Fetch any Patient/Episode specified in the URL params
        if 'patient_id' in k:
            save_kwargs['patient'] = Patient.objects.get(pk=k['patient_id'])

        if 'episode_id' in k:
            save_kwargs['episode'] = Episode.objects.get(pk=k['episode_id'])

        save_kwargs['data'] = self.form_instance.pre_save(**save_kwargs)

        patient, episode = self.form_instance.save(**save_kwargs)
        return self.form_instance.get_redirect_url(patient=patient, episode=episode)


class SubrecordFormView(FormView):

    def dispatch(self, *a, **k):
        if not hasattr(self, 'model'):
            model_name = k['model']
            self.model = subrecords.get_subrecord_from_model_name(model_name)
        return super().dispatch(*a, **k)

    def get_form(self, *a, **k):
        model_name = k['model']
        userland_form = Form.get(f'{model_name}Form')
        if userland_form:
            return userland_form

        class GeneratedForm(SubrecordForm):
            model        = self.model
            display_name = f'{self.verb} {model.get_display_name()}'

        return GeneratedForm


class CreateSubrecordView(SubrecordFormView):
    verb          = 'Add'
    template_name = 'opal/forms/create_subrecord.html'


class EditSubrecordView(SubrecordFormView):
    verb          = 'Edit'
    template_name = 'opal/forms/edit_subrecord.html'

    def dispatch(self, *a, **k):
        model_name = k['model']
        self.model = subrecords.get_subrecord_from_model_name(model_name)
        instance = self.model.objects.get(pk=k['pk'])
        self.form_instance = self.get_form(*a, **k)(instance=instance)

        result = super().dispatch(*a, **k)
        return result
