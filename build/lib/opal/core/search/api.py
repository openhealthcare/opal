from opal.core.views import json_response
from opal.core import schemas
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


class ExtractSchemaViewSet(viewsets.ViewSet):
    """
    Returns the schema to build our extract query builder
    """
    base_name = 'extract-schema'
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        return json_response(schemas.extract_schema())
