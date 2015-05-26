# OPAL Lookup Lists

Lookup Lists allow us to reference lists of available terminology as a foreign key, while
also allowing synonymous terms, and free text options.

# Adding a lookup list

Lookup lists are subclasses of `opal.core.lookuplists.LookupList`. Typically, a specific named
lookup list will not need to do anything other than define a class that inherits from the base
class.

The custom field type `opal.core.fields.ForeignKeyOrFreeText` allows you to build interfaces
that cater for synonyms, and also allow the user to enter a free text string that is not in
the lookup list.

    # yourapp.models

    from django.db import models
    from opal.core import lookuplists
    from opal.core.fields import ForeignKeyOrFreeText
    from opal.models import EpisodeSubrecord

    class TreatmentType(lookuplists.LookupList): pass

    class Treatment(EpisodeSubrecord):
        treatment = ForeignKeyOrFreeText(TreatmentType)
        notes     = models.CharField(max_length=200)
    # yourapp.models


When you create your lookup list, you are creating a new model, so you will need a new migration
to accompany it.

    $ python manage.py schemamigration --atuo yourapp
    $ python manage.py migrate yourapp

The lookup list will automatically be added to the admin.

