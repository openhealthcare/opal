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

