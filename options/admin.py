from django.contrib import admin
from options.models import Destination

class DestinationAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']

admin.site.register(Destination, DestinationAdmin)
