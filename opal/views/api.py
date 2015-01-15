"""
Public facing API views
"""
from django.views.generic import View

from opal.utils.views import _get_request_data, _build_json_response

class APIAdmitEpisodeView(View):
    """
    Admit an episode from upstream!
    """
    def post(self, *args, **kwargs):
        data = _get_request_data(self.request)
        print data
        resp = {'ok': 'Got your admission just fine - thanks!'}
        return _build_json_response(resp)


class APISubrecordDetailView(View):
    """
    Main API entrypoint for Subrecords. 
    """

    def dispatch(self, *args, **kwargs):
        """
        Try to find our subrecord if we're not POSTING?

        404 Appropriately.        
        """

    def get(self, *args, **kwargs):
        """
        Just render the JSON for this subrecord!
        """
        return

    def post(self, *args, **kwargs):
        """
        Create a subrecord
        """
        return

    def put(self, *args, **kwargs):
        """
        Update a subrecord
        """
        return

    def delete(self, *args, **kwargs):
        """
        Delete a subrecord
        """
