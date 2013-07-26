from django.contrib import admin
import reversion

from patients import models

class MyAdmin(reversion.VersionAdmin): pass

class SubRecordAdmin(reversion.VersionAdmin):
    list_filter =['patient']

admin.site.register(models.Patient, MyAdmin)
admin.site.register(models.Tagging, SubRecordAdmin)
admin.site.register(models.Demographics, SubRecordAdmin)
admin.site.register(models.Location, SubRecordAdmin)
admin.site.register(models.Diagnosis, SubRecordAdmin)
admin.site.register(models.PastMedicalHistory, SubRecordAdmin)
admin.site.register(models.GeneralNote, SubRecordAdmin)
admin.site.register(models.Travel, SubRecordAdmin)
admin.site.register(models.Antimicrobial, SubRecordAdmin)
admin.site.register(models.MicrobiologyInput, SubRecordAdmin)
admin.site.register(models.Todo, SubRecordAdmin)
admin.site.register(models.MicrobiologyTest, SubRecordAdmin)
