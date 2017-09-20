from opal.core.views import json_response
from opal.core.api import LoginRequiredViewset
from opal.core.search import schemas
from opal.core.search.extract import ExtractCsvSerialiser


class ExtractSchemaViewSet(LoginRequiredViewset):
    """
    Returns the schema to build our extract query builder
    """
    base_name = 'extract-schema'

    def list(self, request):
        return json_response(schemas.extract_schema())


class DataDictionaryViewSet(LoginRequiredViewset):
    """
    Returns data dictionary for the extract slice
    """
    base_name = 'data_dictionary'

    def list(self, request):
        return json_response(ExtractCsvSerialiser.get_data_dictionary_schema())
