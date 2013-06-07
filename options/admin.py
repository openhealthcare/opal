from django.contrib import admin
from django.contrib.contenttypes import generic
from options.models import option_models, Synonym

class SynonymInline(generic.GenericTabularInline):
    model = Synonym

class OptionAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']
    inlines = [SynonymInline]

for model in option_models.values():
    admin.site.register(model, OptionAdmin)
