"""
Opal Middlewares
"""
from django.utils.deprecation import MiddlewareMixin
# Hat tip:
# http://kevinzhang.org/posts/django-angularjs-and-csrf-xsrf-protection.html

ANGULAR_HEADER_NAME = 'HTTP_X_XSRF_TOKEN'


class AngularCSRFRename(MiddlewareMixin):
    def process_request(self, request):
        if ANGULAR_HEADER_NAME in request.META:
            token = request.META[ANGULAR_HEADER_NAME]
            request.META['HTTP_X_CSRFTOKEN'] = token
            del request.META[ANGULAR_HEADER_NAME]


class DjangoReversionWorkaround(MiddlewareMixin):
    def process_request(self, request):
        access = request.user.is_authenticated  # noqa:
