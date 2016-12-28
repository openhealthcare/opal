## Opal Schemas

Opal schemas provide a JSON representation of the structure of subrecords. Opal uses these schemas internally to construct the `Item` classes in AngularJS on the client side.

The Schema for an Opal application is available at the url `/api/v0.1/schema/` and contains the serialized representation of all subrecords and their fields.

### Subrecord information

Individual subrecords are serialized to the schema using the function `opal.core.schemas.serialize_model`.

#### Schema Subrecord fields

* name: the result of `Subrecord.get_api_name()`
* display_name: the result of `Subrecord.get_display_name()`
* single: Whether the Subrecord is a singleton
* advanced_searchable: if the Subrecord should appear in the advanced search view
* fields: a represention of each field 

Optional fields:

* sort: an Angular string that describes how subrecord of this type should be ordered
* readOnly: if this Subrecord is read only
* form_url: the url of the form of this Subrecord
* icon: the icon class of this Subrecord if it exists
* angular_service: an Angular service used to initialize the `Item` in the Opal client side application.

``` python

  class Colour(models.EpisodeSubrecord):
      _advanced_searchable = False
      _exclude_from_extract = True
      _angular_service = 'Colour'
      _icon = "fa fa-comments"
      name = dmodels.CharField(max_length=200)

# becomes:...
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

### Subrecord Field information

Opal makes the most out of the rich Django model interface by delivering much of the derivable metadata about the structure of fields straight from the model.

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

    # becomes...
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
