## The Test Helper Service

Opal provides a utility to help you test javascript unit tests.

To bring it in, import the module and inject the service.

``` js

  var testHelper;

  beforeEach(function(){
    module('opal.controllers');
    inject(function($injector){
      testHelper = $injector.get('testHelper');
    });
  });
```

The helper has the following functions.

`newEpisode` provides a new episode. It needs to passed in rootScope as as part
of getting a new episode we update the rootSchema to have the schema
information about subrecords.

`getEpisodeData` provides the raw data as pull in from the episode api.


##### Data Loaders

`getRecordLoader` provides a mocked up version of the recordloader that
behaves like the normal recordloader. It comes with the `load` function
already spied on.

`getRecordLoaderData` provides example raw data as pulled from `/api/v0.1/record/`


`getMetaDataLoader` provides a mocked up version of the Metadata that
behaves like the normal Metadata. It comes with the `load` function
already spied on.

`getMetaDataLoader` provides example raw data as pulled from `/api/v0.1/metadata/`


`getReferenceDataLoader` provides a mocked up version of the Referencedata that
behaves like the normal Referencedata. It comes with the `load` function
already spied on.

`getReferenceData` provides example raw data as pulled from `/api/v0.1/referencedata/`

`getUserProfileLoader` provides a mocked up version of the UserProfile that
behaves like the normal UserProfile. It comes with the `load` function
already spied on.

`getUserProfile` provides example raw data as pulled from `/api/v0.1/userprofile/`
