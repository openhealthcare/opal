
# Adding a lookup list

Lookup lists are subclasses of opal.utils.models.LookupList which have a generic relation to Synonym and define a foreign key on the calling model.

You can define them yourself, or use the helper function ```opal.core.lookuplists.lookup_list```

    ColourLookupList = type(*lookup_list('colour', module=__name__))

You can then reference the list in a django model by using a ForeignKeyOrFreeTextField 
You can access the list in an angular template (For autocompletion) where it will be $NAME_list.

e.g. The conditions lookup list is condition_list and used by the elCID Diagnosis model
(https://github.com/openhealthcare/elcid/blob/master/elcid/models.py#L109)

As you are creating a new model, you will need a new migration to accompany it. 

If you have initial values for your lookup list, feel free to add them as a data migration. 

The lookup list will automatically be added to the admin.

so e.g. $ python manage.py schemamigration --atuo opal
