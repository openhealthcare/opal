from django.contrib import admin
import reversion

from patients import models

class MyAdmin(reversion.VersionAdmin): pass


admin.site.register(models.Patient, MyAdmin)
admin.site.register(models.Tagging, MyAdmin)
admin.site.register(models.Demographics, MyAdmin)
admin.site.register(models.Location, MyAdmin)
admin.site.register(models.Diagnosis, MyAdmin)
admin.site.register(models.PastMedicalHistory, MyAdmin)
admin.site.register(models.GeneralNote, MyAdmin)
admin.site.register(models.Travel, MyAdmin)
admin.site.register(models.Antimicrobial, MyAdmin)
admin.site.register(models.MicrobiologyInput, MyAdmin)
admin.site.register(models.Todo, MyAdmin)
admin.site.register(models.MicrobiologyTest, MyAdmin)
