"""
Combined admin for OPAL models
"""
from django.contrib import admin
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

import reversion

from opal.models import option_models, Synonym
from opal.models import UserProfile

from opal import models

admin.site.unregister(User)

class UserProfileInline(admin.StackedInline):
    model = UserProfile

class UserProfileAdmin(UserAdmin):
    inlines = [ UserProfileInline, ]

class MyAdmin(reversion.VersionAdmin): pass

class EpisodeAdmin(reversion.VersionAdmin):
    list_display = ['patient', 'active', 'date_of_admission', 'discharge_date']
    list_filter = ['active', 'patient', ]
    search_fields = ['patient__demographics__name', ]

class PatientAdmin(reversion.VersionAdmin):
    search_fields = ['demographics__name', 'demographics__hospital_number']

class PatientSubRecordAdmin(reversion.VersionAdmin):
    list_filter = ['patient']

class EpisodeSubRecordAdmin(reversion.VersionAdmin):
    list_filter = ['episode']

class SynonymInline(generic.GenericTabularInline):
    model = Synonym

class OptionAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']
    inlines = [SynonymInline]

for model in option_models.values():
    admin.site.register(model, OptionAdmin)

admin.site.register(User, UserProfileAdmin)
admin.site.register(models.Patient, PatientAdmin)
admin.site.register(models.Episode, EpisodeAdmin)

for subclass in models.PatientSubrecord.__subclasses__():
    admin.site.register(subclass, PatientSubRecordAdmin)

for subclass in models.EpisodeSubrecord.__subclasses__():
    admin.site.register(subclass, EpisodeSubRecordAdmin)
