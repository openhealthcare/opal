## OPAL Schemas

Opal schemas serialise subrecords over to the front end for use in the front end.

All subrecords are serialised and there fields are serialised.

#### Model level information

serialises to

* name: the models api name
* display_name: the result of model.get_display_name
* single: if the model is a singleton
* advanced_searchable: if the model appears in the advanced search view
* fields: a represention as denoted below of each field serialised

optionally serialised fields
* sort: an angular string that describes how subrecord of this type should be ordered
* readOnly: if this model is read only
* form_url: the url of the form of this subrecord
* icon: the icon class of this subrecord if it exists
* angular_service: an angular service made up of a service that get's called with the item as the first argument

for example
``` python

  class Colour(models.EpisodeSubrecord):
      _advanced_searchable = False
      _exclude_from_extract = True
      _angular_service = 'Colour'
      _icon = "fa fa-comments"
      name = dmodels.CharField(max_length=200)

# get's serialised to...
  {
    'advanced_searchable': False,
    'angular_service': 'Colour',
    'display_name': 'Colour',
    'fields': [
      # field information as noted below
    ],
    'form_url': u'/templates/forms/colour.html',
    'icon': 'fa fa-comments',
    'name': 'colour',
    'single': False
   }

```

#### Field level information
We try to get the most out of the rich django model interface by delivering a lot of the useful information that we have in the models to the front end.

* default: the default value for the field to appear in the form. At present this will accept a callable but won't serialise date/datetime fields.
* model: The name of the model this field relates to.
* lookup_list: For ForeignKeyOrFreeText fields this returns name of the lookup list that relates to this field.
* title: The verbose_name of this field,
* type: The type of field. Allows us to correctly cast fields into moments on the front end.
* name: the api name for the field

``` python
class Birthday(models.PatientSubrecord):
    party = dmodels.DateTimeField(verbose_name="Party Time!" blank=True)
    name = dmodels.CharField(default='Dave', blank=True, null=True)

    # get's serialised to...
    [
      {
        'default': "Dave",
        'lookup_list': None,
        'model': 'Birthday',
        'name': 'name',
        'title': u'Name',
        'type': 'string'
      },
     {
        'default': None,
        'lookup_list': None,
        'model': 'Birthday',
        'name': 'party',
        'title': u'Party Time!',
        'type': 'date_time'
      }
    ]

```
