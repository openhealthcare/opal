# Application Metadata

Applications commonly need to pass data to the front end which is not either clinical
data about a patient or episode of care, or coded [reference data](referencedata.md).

OPAL provides a simple API for working with such data via the `opal.core.metadata.Metadata`
[discoverable](discoverable.md).

### Defining Metadata

Defining metadata uses the same pattern as all [discoverable](discoverable.md) features, we
define a subclass:

```python
from django.conf import settings
from opal.core import metadata

class FavouriteColours(metadata.Metadata):
    slug = 'favourite-colour'

    @classmethod
    def to_dict(klass):
        return {'favourite_colour': settings.FAVOURITE_COLOUR}
```

### Accessing Metadata on the front end

We can access our metadata with the Angular `Metadata` service.

```javascript
// yourapp/routes.js
when('/my/route', {
    controller: 'MyCtrl',
   	resolve: {
           metadata: function(Metadata){ return Metadata; }
   		 }
    }

// yourapp/yourctrl.js
angular.module('yourapp.controllers').controller(
    'MyCtrl', function($scope, metadata){

      $scope.favourite_colour = metadata.favourite_colour;
      console.log($scope.favourite_colour);
      // -> Whatever settings.FAVOURITE_COLOUR is set to

});

```
