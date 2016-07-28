## The OPAL JSON API

OPAL features a rich, self documenting set of open JSON APIs.

OPAL applications are generally simply a collection of Browser-based clients
for these APIs.

OPAL uses Django Rest Framework to provide it's APIs.

You may examine the API of any running OPAL application by navigating to the url `/api/v0.1/`

### Adding your own APIs

You can add your own APIs to the OPAL API namespace [from plugins](plugins.md#adding-apis) or
by registering them directly with the router.

    from rest_framework.viewsets import ViewSet
    from rest_framework.response import Response
    from opal.core.api import router


    class PingViewSet(ViewSet):
        def list(self, request): return Response('pong')

    router.register('ping', PingViewSet)

### Authentication

OPAL uses
[Django Rest Framework](http://www.django-rest-framework.org/) (DRF) to
provide APIs. DRF ships with multiple authentication
mechanisms which are highly configurable. By default, OPAL applications (e.g. created with
the OPAL scaffolding) will enable Sesison and Token based authentication.

More details on DRF authentication are available in
[their excellent documentation](http://www.django-rest-framework.org/api-guide/authentication/).

#### Session Based
Session based authentication enables users logged in via the standard Django auth mechanism
to use the API. This is what most OPAL applications in the browser will use.

#### Token Based
Token based authentication is targetted at other applications consuming the OPAL API, and
requires the application to pass an API token as a header. These tokens must be associated
with a Django user, and can be created in the Django Admin.

An example of a client using token based authentication is found in the
[OPALAPI](https://github.com/openhealthcare/opalapi) project.
