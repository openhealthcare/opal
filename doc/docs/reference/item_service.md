## The Item service

The `Item` service in `opal.services` provides us with core functionality related
to interacting with subrecord in the client.

### Methods

#### Item.makeCopy

Returns a clone of the editable fields + consistency token so that
we can then update them in isolation elsewhere.

The copy of item has an _local object. This contains the uniqueName used by the object in form fields, and can be used to contain any other variables that you do not want sent back to the server.

#### Item.save

Saves attributes to the server.

    item.save(data_to_save);

#### Item.formController

The Angular controller used by the modal that is opened when you edit this item to allow custom logic.

Defaults to 'EditItemCtrl';
