from django.contrib import admin
import reversion

from patients import models

# TODO why can't we use use reversion.VersionAdmin?
class MyAdmin(reversion.VersionAdmin): pass

class PatientSubRecordAdmin(reversion.VersionAdmin):
    list_filter = ['patient']

class EpisodeSubRecordAdmin(reversion.VersionAdmin):
    list_filter = ['episode']

admin.site.register(models.Patient, MyAdmin)
admin.site.register(models.Episode, MyAdmin)

for subclass in models.PatientSubrecord.__subclasses__():
    admin.site.register(subclass, PatientSubRecordAdmin)

for subclass in models.EpisodeSubrecord.__subclasses__():
    admin.site.register(subclass, EpisodeSubRecordAdmin)
