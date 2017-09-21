from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from opal.core.views import json_response
from opal.core.search import schemas
from opal.core.search.extract import ExtractCsvSerialiser


class ExtractSchemaViewSet(viewsets.ViewSet):
    """
    Returns the schema to build our extract query builder
    """
    base_name = 'extract-schema'
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        return json_response(schemas.extract_schema())


class DataDictionaryViewSet(viewsets.ViewSet):
    """
    Returns data dictionary for the extract slice
    """
    base_name = 'data-dictionary'
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        return json_response(ExtractCsvSerialiser.get_data_dictionary_schema())
