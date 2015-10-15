## The Item service

The `Item` service in `opal.services` provides us with core functionality related
to interacting with subrecord in the client.

### Methods

#### Item.makeCopy

Returns a clone of the editable fields + consistency token so that
we can then update them in isolation elsewhere.

#### Item.save

Saves attributes to the server.

    item.save(data_to_save);
