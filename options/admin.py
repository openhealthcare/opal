from django.contrib import admin
from options.models import option_models

class OptionAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']

for model in option_models.values():
    admin.site.register(model, OptionAdmin)
