# Working with Clinical Data in Angular

Opal provides a range of Angular services for working with clinical data on
the front end.

## The Episode Service

The `Episode` Service will return an Episode object that represents an individual
episode of care, and provides various methods for interacting with both episodes and
subrecords.

```js
var episode = new Episode(my_episode_data);
var editing = episode.makeCopy();
editing.start_date = new Date();
episode.save(editing);
```

## The Item Service

The `Item` Service returns Item objects that represent individual instances of
subrecords. They must be initialised with an episode and a schema representing
the available data fields for this subrecord type.

```js
var diagnosis = new Item({}, episode, $rootScope.fields.diagnosis);
var editing = diagnosis.makeCopy();
editing.date_of_diagnosis = new Date();
diagnosis.save(editing);
```

## Subrecord CRUD modals

The `Episode` service has a convenient API that allows you to open a modal to edit
a new or existing subrecord.

```js
epiode.recordEditor.newItem('diagnosis'):
// -> Opens a modal with the diagnosis form and will create a new diagnosis on save

episode.recordEditor.editItem('diagnosis', 0);
// -> Opens a modal that allows the user to edit the first diagnosis

episode.recordEditor.deleteItem('diagnosis', 0);
// -> Prompts the user to confirm the deletion of the first diagnosis
```

## Customising Subrecords

Sometimes our application will wish to customise a subrecord of a particular type - for
instance to set default values. We do this by setting a custom record service.


First, we set the name of the service to use as a constructor for this record type as
a property on the model.

```python
# yourapp/models.py
class Diagnosis(models.Diagnosis):
    _angular_service = 'Diagnosis'
```

Next we must include the file with our new service in our application.

```python
# yourapp/__init__.py
class YourApp(application.OpalApplication):
    javascripts = [..., 'js/diagnosis.js', ...]
```

Finally we define an Angular service which expects to be passed the record in order
to set defaults.

```js
// yourapp/static/js/diagnosis.js
angular.module('opal.records').factory('Diagnosis', function(){
    return function(record){
        if(!record.date_of_diagnosis){ record.date_of_diagnosis = moment()}
        return record;
    }
});

```
