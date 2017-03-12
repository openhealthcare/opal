"""
Combined admin for Opal models
"""
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ValidationError
from django import forms

import reversion

from opal import models
from opal.models import Synonym
from opal.models import UserProfile
from opal.core.lookuplists import LookupList, synonym_exists
from opal.core.subrecords import episode_subrecords, patient_subrecords

admin.site.unregister(User)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    filter_horizontal = ('roles',)


class FilterInline(admin.StackedInline):
    model = models.Filter


class UserProfileAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'first_name',
                'last_name', 'email',
                'password1', 'password2'
            )
        }),
    )
    inlines = [UserProfileInline, FilterInline, ]


class MyAdmin(reversion.VersionAdmin):
    pass


class EpisodeAdmin(reversion.VersionAdmin):
    list_display = [
        'patient', 'active', 'date_of_admission', 'discharge_date'
    ]
    list_filter = ['active', ]
    search_fields = [
        'patient__demographics__first_name',
        'patient__demographics__surname',
        'patient__demographics__hospital_number'
    ]


class PatientAdmin(reversion.VersionAdmin):
    search_fields = [
        'demographics__first_name',
        'demographics__surname',
        'demographics__hospital_number'
    ]


class TaggingAdmin(reversion.VersionAdmin):
    list_display = ['value', 'episode']


class PatientSubrecordAdmin(reversion.VersionAdmin):
    search_fields = [
        'patient__demographics__first_name',
        'patient__demographics__surname',
        'patient__demographics__hospital_number',
    ]


class EpisodeSubrecordAdmin(reversion.VersionAdmin):
    search_fields = [
        'episode__patient__demographics__first_name',
        'episode__patient__demographics__surname',
        'episode__patient__demographics__hospital_number',
    ]


class SynonymInline(GenericTabularInline):
    model = Synonym


class LookupListForm(forms.ModelForm):

    def clean_name(self):
        object_class = self.instance.__class__
        name = self.cleaned_data["name"]
        if synonym_exists(object_class, name):
            raise ValidationError(
                "A synonym of that name already exists"
            )

        return self.cleaned_data["name"]


class OptionAdmin(admin.ModelAdmin):
    form = LookupListForm
    ordering = ['name']
    search_fields = ['name']
    inlines = [SynonymInline]


for model in LookupList.__subclasses__():
    admin.site.register(model, OptionAdmin)

admin.site.register(User, UserProfileAdmin)
admin.site.register(models.Patient, PatientAdmin)
admin.site.register(models.Episode, EpisodeAdmin)
admin.site.register(models.Tagging, TaggingAdmin)


for subclass in patient_subrecords():
    if not subclass._meta.abstract and not getattr(
            subclass, "_no_admin", False):
        admin.site.register(subclass, PatientSubrecordAdmin)

for subclass in episode_subrecords():
    if not subclass._meta.abstract and not getattr(
            subclass, "_no_admin", False):
        admin.site.register(subclass, EpisodeSubrecordAdmin)

admin.site.register(models.ContactNumber, MyAdmin)
admin.site.register(models.Role, MyAdmin)
admin.site.register(models.Macro, MyAdmin)
