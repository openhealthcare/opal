## The OPAL JSON API

OPAL features a rich, self documenting set of open JSON APIs.

OPAL applications are generally simply a collection of Browser-based clients
for these APIs.

OPAL uses Django Rest Framework to provide it's APIs.

You may examine the API of any running OPAL application by navigating to the url `/api/v0.1/`

### Adding your own APIs

You can add your own APIs to the OPAL API namespae [from plugins](plugins.md#adding-apis) or 
by registering them directly with the router.

    from rest_framework.viewsets import ViewSet
    from rest_framework.response import Response
    from opal.core.api import router
    

    class PingViewSet(ViewSet):
        def list(self, request): return Response('pong')

    router.register('ping', PingViewSet)
