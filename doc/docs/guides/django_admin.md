# Working with the Django Admin

One of the great features of Django is the
[Admin application](https://docs.djangoproject.com/en/1.10/ref/contrib/admin/) it provides for
developers and administrators.

By default, you can access the Django admin by visiting the `/admin/` url of your application.

Opal will automatically register Patients, Episodes, Lookup lists, and all Subrecords with the
Django Admin for you.

## Customising the Admin

If you need to customise the admin for a particular subrecord you will need to 'unregister' the
admin class that Opal has registered it with.

```python
# myapp/admin.py
from django.contrib import admin
from opal.admin import EpisodeSubrecordAdmin
from myapp import models

admin.site.unregister(models.Diagnosis)

class DiagnosisAdmin(EpisodeSubrecordAdmin):
  list_display = ['__unicode__', 'condition']

admin.site.register(models.Diagnosis, DiagnosisAdmin)
```

It is strongly suggested that any custom Admin implementation inherits from the Django
Reversion `ReversionAdmin` base class. It is through this registering step that our automatic
audit trail is enabled for a particular model.

The base subrecord admin classes `opal.admin.EpisodeSubrecordAdmin` and
`opal.admin.PatientSubrecordAdmin` allow searching by basic patient demographics (name,
identifier), and also inherits from `ReversionAdmin`.
