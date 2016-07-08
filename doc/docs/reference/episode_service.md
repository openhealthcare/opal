## The Episode service

The `Episode` service in `opal.services` provides us with core functionality related
to interacting with episodes in the client.

### Constructor

The Episode service is instantiated with the Episode data that comes back from the
Episode JSON API.

    var episode = new Episode(json_data);


### Methods

#### Episode.getTags

Return a list of the current tags this episode has as strings.

    episode.getTags();
    // ['mine', 'infectioncontrol']

#### Episode.hasTag

Predicate function that determines whether the episode is tagged with a given tag.

Arguments:

* `tag`: The tag you are interested in.


#### Episode.newItem

Instantiate a new subrecord for this episode of a given type.

Arguments:

* `recordName`: The name of the type of record you want to instantiate.

Example usage:

    episode.newItem('diagnosis');
    // item (an Item() instance.


#### Episode.recordEditor.newItem(name)

Takes a string, opens a modal from which the user can create a new subrecord of type `name`.

```js
epiode.recordEditor.newItem('diagnosis'):
// -> Opens a modal with the diagnosis form and will create a new diagnosis on save
```

#### Episode.recordEditor.deleteItem(name, index)

Delete the `index-th` item of type `name`. Prompt the user to confirm this with a dialog.

```js
episode.recordEditor.deleteItem('diagnosis', 0);
// -> Prompts the user to confirm the deletion of the first diagnosis
```
#### Episode.recordEditor.editItem(name, index)

Open a modal from which the user may edit the `index-th` item of type `name`.

```js
episode.recordEditor.editItem('diagnosis', 0);
// -> Opens a modal that allows the user to edit the first diagnosis
```
