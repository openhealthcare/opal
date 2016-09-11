## Reference data

Lookup Lists allow us to create or reference canonical lists of available terminology as a
foreign key, while also allowing synonymous terms, and a free text override.

### Adding a lookup list

Lookup lists are subclasses of `opal.core.lookuplists.LookupList`. Typically, a specific named
lookup list will not need to do anything other than define a class that inherits from the base
class.

The custom field type `opal.core.fields.ForeignKeyOrFreeText` allows you to build interfaces
that cater for synonyms, and also allow the user to enter a free text string that is not in
the lookup list.

```python
# yourapp.models
from django.db import models
from opal.core import lookuplists
from opal.core.fields import ForeignKeyOrFreeText
from opal.models import EpisodeSubrecord

class TreatmentType(lookuplists.LookupList): pass

class Treatment(EpisodeSubrecord):
    treatment = ForeignKeyOrFreeText(TreatmentType)
    notes     = models.CharField(max_length=200)
```

When you create your lookup list, you are creating a new model, so you will need a new migration
to accompany it.

```bash
$ python manage.py schemamigration --atuo yourapp
$ python manage.py migrate yourapp
```

The lookup list will automatically be added to the admin.

### Reference data JSON API

Reference data is available over the OPAL JSON API.

You may either load all lookuplists at once via the `/api/v0.1/referencedata/` endpoint, or
individual lookuplists by name - for example all diagnoses from `/api/v0.1/referencedata/diagnosis/`.

The reference data API also loads all synonyms in a flat list - the conversion of synonyms to their
canonical form is handled by the save mechanism of subrecords using `ForeignKeyOrFreeText` fields.

### Working with reference data on the front end

The Angular service `Referencedata` can be used to fetch all lookuplists at once - for instance
loaded in the Angular routing for a controller in your application

```javascript
when('/my/route', {
    controller: 'MyCtrl',
   	resolve: {
           referencedata: function(Referencedata){ return Referencedata; }
   		 }
    }
```

Lookuplists will then be available either as properties of the `referencedata` object.

### Using referencedata in forms

The OPAL [form templatetag library](../reference/form_templatetags.md) allow us to easily incorporate
referencedata into the forms we build, eiether by detecting their use automatically when we have
`ForeignKeyOrFreeText` fields, or explicitly by passing an argument.

```html
{% load forms %}
{% input field="Diagnosis.condition" %}
{% select label="List of Conditions" lookuplist="referencedata.diagnosis" %}
```

### Management commands

OPAL ships with some managemnent commands for importing and exporting lookup lists

#### dump_lookup_lists

Prints all lookuplists as JSON to stdout.

#### load_lookup_lists

Loads lookup lists from all plugins/apps in the OPAL JSON format. The lookup lists are expected to be in
{{ app }}/data/lookuplists.json

#### delete_all_lookuplists

Deletes all currently lookuplist values and related synonyms
