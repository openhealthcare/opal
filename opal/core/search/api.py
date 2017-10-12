from opal.core.views import json_response
from opal.core import schemas
from rest_framework import viewsets


class ExtractSchemaViewSet(viewsets.ViewSet):
    """
    Returns the schema to build our extract query builder
    """
    base_name = 'extract-schema'

    def list(self, request):
        return json_response(schemas.extract_schema())
