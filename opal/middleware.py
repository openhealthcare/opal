"""
Opal Middlewares
"""
from django.utils.deprecation import MiddlewareMixin


class DjangoReversionWorkaround(MiddlewareMixin):
    def process_request(self, request):
        access = request.user.is_authenticated  # noqa:
