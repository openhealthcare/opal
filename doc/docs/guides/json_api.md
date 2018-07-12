## The Opal JSON API

Opal features a rich, self documenting set of open JSON APIs.

Opal applications are generally simply a collection of Browser-based clients
for these APIs.

Opal uses Django Rest Framework to provide it's APIs.

You may examine the API of any running Opal application by navigating to the url `/api/v0.1/`

### Adding your own APIs

You can add your own APIs to the Opal API namespace [from plugins](plugins.md#adding-apis) or
by registering them directly with the router.

```python
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from opal.core.api import router


class PingViewSet(ViewSet):
    def list(self, request): return Response('pong')

router.register('ping', PingViewSet)
```

APIs can make use of method decorators `item_from_pk`, `episode_from_pk` and `patient_from_pk` that will replace a pk passed into a method with self.model, Episode or Patient respectively.

e.g.

```python
class SomeBespokeViewset(viewsets.Viewset):
  model = ClinicalInformation

  @item_from_pk
  def some_api_endpoint(self, request, clinical_information):
    # Some logic
```

### Authentication

Opal uses
[Django Rest Framework](http://www.django-rest-framework.org/) (DRF) to
provide APIs. DRF ships with multiple authentication
mechanisms which are highly configurable. By default, Opal applications (e.g. created with
the Opal scaffolding) will enable Session and Token based authentication.

More details on DRF authentication are available in
[their excellent documentation](http://www.django-rest-framework.org/api-guide/authentication/).


### Permissioning

Opal uses the DRF permissions system for JSON APIs.

Opal ships with `opal.core.api.LoginRequiredViewset` which adds the permission class
IsAuthenticated by default. Developers are strongly encouraged to ensure that APIs which
serve patient data are restricted to logged in users.

More details on DRF permissions are available [in the DRF documentation](http://www.django-rest-framework.org/api-guide/permissions/)
.

#### Session Based
Session based authentication enables users logged in via the standard Django auth mechanism
to use the API. This is what most Opal applications in the browser will use.

#### Token Based
Token based authentication is targeted at other applications consuming the Opal API, and
requires the application to pass an API token as a header. These tokens must be associated
with a Django user, and can be created in the Django Admin.

An example of a client using token based authentication is found in the
[OpalAPI](https://github.com/openhealthcare/opalapi) project.
