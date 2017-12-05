## Default context processors

Context processors are part of the Django template language. In Opal we use this to give all templates access to some generic information about the internals of Opal applications.

### Settings
All Opal settings are copied into the context of the template.

### Models
All [subrecords](../reference/subrecords/) (the underlying clinical models of Opal) are copied into the context of the template under the namespace `models`, e.g. the Allergies subrecord can be referred to by `models.Allergy`

### Pathways
Pathways are copied in to the context of the template under the namespace `pathways`. For an example Pathway you would be able to access attributes of a Pathway thus: `pathways.MyPathway.get_display_name`

It is important to note that since the context processor is applied *after* the request context, this can lead to the context processor over-writing elements of context data. For further information on this see the Django documentation.
