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
