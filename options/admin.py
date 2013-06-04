from django.contrib import admin
from options.models import Antimicrobial, Destination

class AntimicrobialAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']

class DestinationAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']

admin.site.register(Antimicrobial, AntimicrobialAdmin)
admin.site.register(Destination, DestinationAdmin)
